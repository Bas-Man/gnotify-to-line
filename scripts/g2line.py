"""A program to send notification through LINE based on Email received."""
import argparse
import os
from pathlib import Path
import sys
from typing import Dict, Optional

dov_env = True
try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    dov_env = False
    print('borked!')

from gmail2line import config_parser
from gmail2line import glogger
from gmail2line import line
from gmail2line import find_matches
from gmail2line.cli import ExitCodes
from gmail2line.cli import health
from gmail2line.gmail import resource, mail, label
from gmail2line.messages import common

if dov_env:
    load_dotenv()

NAME = os.getenv('NAME_1')

PICKLE = 'token.pickle'
CONFIG_DIR = Path.home() / '.config' / 'gmail-notify'
TOML_FILE = CONFIG_DIR / 'config.toml'

# Read TOML Configuration File
config = config_parser.load_toml(TOML_FILE)


def command():
    """
    Document me
    """
    parse = argparse.ArgumentParser()
    parse.add_argument('-l', '--label', help='Lookup the ID for LABEL.')
    parse.add_argument(
        '-la',
        '--label-all',
        help='List all labels in Gmail.',
        action='store_true',
    )
    parse.add_argument(
        '-ln',
        '--label-new',
        help='Register a new label with Gmail.',
        action='store_true',
    )
    parse.add_argument(
        '--health',
        help='Check for configuration files and Gmail connection',
        action='store_true',
    )
    parse.add_argument(
        '--suppressed',
        help='Process message, but suspress notifications.',
        action='store_true',
    )
    args = parse.parse_args()

    logger = glogger.setup_logging(CONFIG_DIR, config['log'].get('lvl'))
    if args.label_all:
        label.list_all_labels_and_ids(
            resource.get_resource(CONFIG_DIR), logger
        )
    elif args.label:
        label.lookup_label_id(resource.get_resource(CONFIG_DIR), logger, args)
    elif args.label_new:
        label.setup_new_label(resource.get_resource(CONFIG_DIR))
    elif args.health:
        health.check_health(CONFIG_DIR)
    else:
        # Default: Sanity check and call process()
        label_id = os.getenv('LABEL_ID')
        if label_id is None:
            logger.error('No Label ID found. Unable to process any message.')
            logger.info('Processing ending early.')
            sys.exit(ExitCodes.NO_LABEL_ID)
        else:
            line_token = os.getenv('LINE_TOKEN_PERSONAL')
            if line_token is None:
                logger.error(
                    'No LINE Access Token found. Unable to send LINE messages.'
                )
                logger.error('Unable to process messages.')
                logger.info('Processing ending early.')
                sys.exit(ExitCodes.NO_LINE_ACCESS_TOKEN)
            else:
                process(logger, line_token, label_id, args.suppressed)


def get_persons_name(data: dict) -> Optional[str]:
    """
    This function looks up the preferred name of the person if possible.
    If no match for the name in the lookup table is found. The name in the email
    will be used. if no name is found then None is returned.

    :param data: The data dict returned after the email has been parsed. Should contain \
    a key of 'name'
    :type data: dict
    :returnes: The standardized name or the name in the email or None
    """
    name: Optional[str] = None
    aliases: Optional[Dict[str, str]] = config_parser.build_name_lookup(config)
    if aliases:
        name = config_parser.lookup_name(aliases, data.get('name'))
        if name is None and data.get('name') is not None:
            name: Optional[str] = data.get('name')
    return name


def post_processing_gmail_labelling(
    logger,
    gmail_resource,
    message_id: str,
    processed_label,
    service: str,
) -> None:
    """
    This function handles adding the 'notified' label to the message after it
    has been processed. It optionally will mark the message as 'archived'
    if specified in the configuration file.

    :param logger: The logger handle.
    :type logger: Object
    :param gmail_resource: Gmail API handle
    :type gmail_resource: Object
    :param message_id: Internal Gmail message ID
    :type message_id: str
    :param service: The service that sent the original email. Bus, Train or other.
    :type service: str
    :returns: None
    """
    # Mail was processed. Add label so its not processed again
    # Gmail only allows for the shortest time interval of one day.
    logger.debug('adding label')
    label.add_label_to_message(gmail_resource, message_id, processed_label)
    if config_parser.should_mail_be_archived(
        config_parser.gmail_archive_setting(config),
        config_parser.service_archive_settings(config, service),
    ):
        label.archive_message(service, message_id)


def handle_each_email(gmail_resource, message_id, logger) -> dict:
    """
    Process each message and extract who the notifier is as well as the data
    in the body of the email

    :param gmail_resource: Gmail API connection
    :type gmail_resource: object
    :param message_id: The id of the message to be processed.
    :type message_id: str
    :param logger: The logger object
    :type logger: object
    :return: The data extracted from the email.
    :rtype: dict
    """
    # Get data from config so that it is easier to use.
    _, subjects, sender_service_key = config_parser.senders_subjects(config)
    data: Dict[str, str] = {}
    single_email = mail.get_message(gmail_resource, message_id, logger)
    # Check the subject is an expected notification subject line
    if single_email is not None and 'subject' in single_email:
        subject: str = single_email.get('subject')
        logger.debug(f'Subject: {subject}')
        sender: str = single_email.get('from')
        logger.debug(f'Sender: {sender}')
        if subject in subjects:
            # workout which notification we are dealing with and use the correct
            # regular expression string
            logger.debug('Subject Passed.')
            key = sender_service_key.get(sender)
            if key is not None and key in config['services']:
                if 'regex' in config['services'][key]:
                    regex: str = config['services'][key].get('regex')
                    email_body = single_email.get_content()
                    data: Dict[str, str] = find_matches(email_body, regex)
                    data['notifier'] = key
                    return data
            else:
                # This needs to be logged. Means failed to match sender.
                logger.warning(
                    f'Failed to process message_id: {message_id} '
                    f'Matched Subject: {subject} '
                    f'Sender not matched: {sender}'
                )
                return data

        # Not an expected subject line. Ignore this email
        logger.info('This is not a notification.')
        logger.info(f'sender: {sender}\n\t')
        logger.info(f'subject: {subject}\n')
        logger.debug(f'contents: {single_email.get_content()}\n')
        logger.debug(f'Data: {data}\n')
    return data


def process(
    logger, line_token: str, processed_label: str, suppress_notification: bool
) -> None:  # pylint: disable=too-many-branches,too-many-statements
    """
    This the main function for processing all email messages that match the
    search conditions.
    :param logger:
    :type logger: Object
    :param line_token: Token for accessing LINE notifier
    :type line_token: str
    :param processed_label: Gmail Internal Label ID
    :type processed_labbel: str
    :returns: None
    """
    logger.info('Looking for email for notification')
    g_search = config_parser.gmail_search_string(config)
    gmail_resource = resource.get_resource(CONFIG_DIR)
    if g_search is None:
        logger.info('Search String is not valid. Unable to get messages.')
        sys.exit(ExitCodes.MISSING_GOOGLE_SEARCH_STRING)
    message_ids = mail.get_message_ids(gmail_resource, g_search)
    if not mail.found_messages(message_ids):
        logger.debug('There were no messages.')
        logger.info('Ending cleanly with no messages to process')
        sys.exit(ExitCodes.OK)
    list_of_message_ids = mail.get_only_message_ids(message_ids)
    logger.debug(f'message_ids:\n\t{list_of_message_ids}\n')
    for message_id in list_of_message_ids:
        processed = False
        data = handle_each_email(gmail_resource, message_id, logger)
        logger.debug(data['notifier'].capitalize())
        logger.debug(f'data: {data}\n')
        name: Optional[str] = get_persons_name(data)
        notification_message = common.call_function(name, data)
        if notification_message:
            logger.debug(data['notifier'].capitalize())
            if not suppress_notification:
                line.send_notification(notification_message, line_token)
            else:
                # Suppressing notifications.
                logger.info(
                    f"Message notification for {data['notifier']} has been suppressed."
                )
            processed = True
        else:
            logger.info(
                f"Caller: {data['notifier']} is not a callable function."
            )

        if data.get('notifier') is None and data is not None:
            logger.warning('Subject matched but From was not matched')
        elif data.get('notifier') is None and data is None:
            logger.info('Non-Notification email from expected sender')

        if processed:
            post_processing_gmail_labelling(
                logger,
                gmail_resource,
                message_id,
                processed_label,
                data['notifier'],
            )
            # End of the program
    logger.info('Ending cleanly')


if __name__ == '__main__':
    command()
