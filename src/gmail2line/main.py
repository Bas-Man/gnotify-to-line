""" A program to send notification through LINE based on Email received."""
from pathlib import Path
import sys
import os
import argparse
from typing import Dict, Optional
from dotenv import load_dotenv
import messages
from messages import common, message_builder
import config_parser
from patterns import find_matches
import glogger
import line
import health
from exit_codes import ExitCodes
from gmail import service, mail, label

load_dotenv()
NAME = os.getenv("NAME_1")

PICKLE = "token.pickle"
CONFIG_DIR = Path.home() / ".config" / "gmail-notify"
TOML_FILE = CONFIG_DIR / "config.toml"

# Read TOML Configuration File
config = config_parser.load_toml(TOML_FILE)


def cli():
    """
    Document me
    """
    parse = argparse.ArgumentParser()
    parse.add_argument("-l", "--label", help="Lookup the ID for LABEL.")
    parse.add_argument("-la", "--label-all", help="List all labels in Gmail.",
        action='store_true')
    parse.add_argument("-ln", "--label-new", help="Register a new label with Gmail.",
        action='store_true')
    parse.add_argument("--health",
        help="Check for configuration files and Gmail connection",
        action='store_true')
    args = parse.parse_args()

    logger = glogger.setup_logging(CONFIG_DIR, config['log'].get('lvl'))
    if args.label_all:
        label.list_all_labels_and_ids(service.get_service(CONFIG_DIR), logger)
    elif args.label:
        label.lookup_label_id(service.get_service(CONFIG_DIR), logger, args)
    elif args.label_new:
        label.setup_new_label(service.get_service(CONFIG_DIR))
    elif args.health:
        health.check_health(CONFIG_DIR)
    else:
        # Default: Sanity check and call process()
        label_id = os.getenv('LABEL_ID')
        if label_id is None:
            logger.error("No Label ID found. Unable to process any message.")
            logger.info("Processing ending early.")
            sys.exit(ExitCodes.NO_LABEL_ID)
        else:
            line_token = os.getenv("LINE_TOKEN_PERSONAL")
            if line_token is None:
                logger.error("No LINE Access Token found. Unable to send LINE messages.")
                logger.error("Unable to process messages.")
                logger.info("Processing ending early.")
                sys.exit(ExitCodes.NO_LINE_ACCESS_TOKEN)
            else:
                process(logger, line_token, label_id)


def handle_each_email(service, message_id, logger) -> dict:
    """
    Process each message and extract who the notifier is as well as the data
    in the body of the email

    :param service: Gmail API connection
    :type service: object
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
    single_email = mail.get_message(service, message_id, logger)
    # Check the subject is an expected notification subject line
    if single_email is not None and 'subject' in single_email:
        subject: str = single_email.get("subject")
        logger.debug(f"Subject: {subject}")
        sender: str = single_email.get("from")
        logger.debug(f"Sender: {sender}")
        if subject in subjects:
            # workout which notification we are dealing with and use the correct
            # regular expression string
            logger.debug("Subject Passed.")
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
                logger.warning(f"Failed to process message_id: {message_id} "
                               f"Matched Subject: {subject} "
                               f"Sender not matched: {sender}")
                return data

        # Not an expected subject line. Ignore this email
        logger.info("This is not a notification.")
        logger.info(f"sender: {sender}\n\t")
        logger.info(f"subject: {subject}\n")
        logger.debug(f"contents: {single_email.get_content()}\n")
        logger.debug(f"Data: {data}\n")
    return data


def process(logger, line_token: str, processed_label: str):  # pylint: disable=too-many-branches,too-many-statements
    """
    Document me
    """
    logger.info("Looking for email for notification")
    g_search = config_parser.gmail_search_string(config)
    g_service = service.get_service(CONFIG_DIR)
    if g_search is None:
        logger.info("Search String is not valid. Unable to get messages.")
        sys.exit(ExitCodes.MISSING_GOOGLE_SEARCH_STRING)
    message_ids = mail.get_message_ids(g_service, g_search)
    if not mail.found_messages(message_ids):
        logger.debug("There were no messages.")
        logger.info("Ending cleanly with no messages to process")
        sys.exit(ExitCodes.OK)
    list_of_message_ids = mail.get_only_message_ids(message_ids)
    logger.debug(f"message_ids:\n\t{list_of_message_ids}\n")
    for message_id in list_of_message_ids:
        processed = False
        data = handle_each_email(g_service, message_id, logger)
        logger.debug(data['notifier'].capitalize())
        logger.debug(f"data: {data}\n")
        aliases: Optional[Dict[str, str]] = config_parser.build_name_lookup(config)
        name: Optional[str] = None
        if aliases:
            name = config_parser.lookup_name(aliases, data.get('alias'))
            if name is None and data.get('name') is not None:
                name = data.get('name')
        notification_message = common.call_function(name, data)
        if notification_message:
            logger.debug(data['notifier'].capitalize())
            line.send_notification(notification_message, line_token)
            processed = True
        else:
            logger.info(
                f"Caller: {data['notifier']} is not a callable function."
                )

        if data.get("notifier") is None and data is not None:
            logger.warning("Subject matched but From was not matched")
        elif data.get("notifier") is None and data is None:
            logger.info("Non-Notification email from expected sender")

        if processed:
            # Mail was processed. Add label so its not processed again
            # Gmail only allows for the shortest time interval of one day.
            logger.debug("adding label")
            label.add_label_to_message(
                g_service, message_id, processed_label)
            if config_parser.should_mail_be_archived(
                    config_parser.gmail_archive_setting(config),
                    config_parser.service_archive_settings(
                        config, data['notifier'])
            ):
                label.archive_message(service, message_id)
            # End of the program
    logger.info("Ending cleanly")


if __name__ == '__main__':
    cli()
