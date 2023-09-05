""" A program to send notification through LINE based on Email received."""
from pathlib import Path
import sys
import os
import argparse
from email import parser
from email import policy
from typing import Dict, Optional, Union
from dotenv import load_dotenv
import message_builder
import config_parser
from patterns import find_matches
import glogger
import line
from exit_codes import ExitCodes
import gmail

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
    parse.add_argument("-l", "--label")
    parse.add_argument("-la", "--label-all", action='store_true')
    args = parse.parse_args()

    logger = glogger.setup_logging(CONFIG_DIR, config['log'].get('lvl'))
    if args.label_all:
        gmail.list_all_labels_and_ids(CONFIG_DIR, logger)
    elif args.label:
        gmail.lookup_label_id(CONFIG_DIR, logger, args)
    else:
        # Default: Sanity check and call process()
        LABEL_ID = os.getenv("LABEL_ID")
        if LABEL_ID is None:
            logger.error("No Label ID found. Unable to process any message.")
            logger.info("Processing ending early.")
            sys.exit(ExitCodes.NO_LABEL_ID)
        else:
            ACCESS_TOKEN = os.getenv("LINE_TOKEN")
            if ACCESS_TOKEN is None:
                logger.error("No LINE Access Token found. Unable to send LINE messages.")
                logger.error("Unable to process messages.")
                logger.info("Processing ending early.")
                sys.exit(ExitCodes.NO_LINE_ACCESS_TOKEN)
            else:
                process(logger, ACCESS_TOKEN, LABEL_ID)


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
    single_email = gmail.get_message(service, message_id, logger)
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
        logger.info("This is not a notifcation.")
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
    service = gmail.get_service(CONFIG_DIR)
    g_search = config_parser.gmail_search_string(config)
    if g_search is None:
        logger.info("Search String is not valid. Unable to get messages.")
        sys.exit(ExitCodes.MISSING_GOOGLE_SEARCH_STRING)
    message_ids = gmail.get_message_ids(service, g_search)
    if not gmail.found_messages(message_ids):
        logger.debug("There were no messages.")
        logger.info("Ending cleanly with no messages to process")
        sys.exit(ExitCodes.OK)
    list_of_message_ids = gmail.get_only_message_ids(message_ids)
    logger.debug(f"message_ids:\n\t{list_of_message_ids}\n")
    for message_id in list_of_message_ids:
        processed = False
        data = handle_each_email(service, message_id, logger)
        logger.debug(data['notifier'].capitalize())
        logger.debug(f"data: {data}\n")
        message = message_builder.call_function(NAME, data)
        if message:
            logger.debug(data['notifier'].capitalize())
            line.send_notification(message, line_token)
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
            gmail.add_label_to_message(
                service, message_id, processed_label)
            if config_parser.should_mail_be_archived(
                    config_parser.gmail_archive_setting(config),
                    config_parser.service_archive_settings(
                        config, data['notifier'])
            ):
                gmail.archive_message(service, message_id)
            # End of the program
    logger.info("Ending cleanly")


if __name__ == '__main__':
    cli()
