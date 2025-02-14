"""A program to send notification through LINE based on Email received."""
import argparse
import os
import sys
from pathlib import Path
from typing import Dict, Optional

from dotenv import load_dotenv

from gmail2notification.core.matching import find_matches
from gmail2notification import glogger
from gmail2notification.cli import ExitCodes, health
from gmail2notification.config import parser as config_parser
from gmail2notification.gmail import label, mail, resource
from gmail2notification.messages import builder
from gmail2notification.notifiers.base import NotifierFactory
from gmail2notification.notifiers.line_notifier import LineNotifier  # Required for registration
from gmail2notification.notifiers.pushover_notifier import PushoverNotifier # Required for registration

load_dotenv()

CONFIG_DIR = Path.home() / ".config" / "gmail-notify"
TOML_FILE = CONFIG_DIR / "config.toml"

# Read TOML Configuration File
config = config_parser.load_toml(TOML_FILE)


def command():
    """
    Document me
    """
    parse = argparse.ArgumentParser()
    parse.add_argument("-l", "--label", help="Lookup the ID for LABEL.")
    parse.add_argument(
        "-la",
        "--label-all",
        help="List all labels in Gmail.",
        action="store_true",
    )
    parse.add_argument(
        "-ln",
        "--label-new",
        help="Register a new label with Gmail.",
        action="store_true",
    )
    parse.add_argument(
        "--health",
        help="Check for configuration files and Gmail connection",
        action="store_true",
    )
    parse.add_argument(
        "--suppressed",
        help="Process message, but suspress notifications.",
        action="store_true",
    )
    args = parse.parse_args()

    logger = glogger.setup_logging(CONFIG_DIR, config_parser.get_logging_level(config))
    if args.label_all:
        label.list_all_labels_and_ids(resource.get_resource(CONFIG_DIR), logger)
    elif args.label:
        label.lookup_label_id(resource.get_resource(CONFIG_DIR), logger, args)
    elif args.label_new:
        label.setup_new_label(resource.get_resource(CONFIG_DIR))
    elif args.health:
        health.check_health(CONFIG_DIR)
    else:
        # Default: Sanity check and call process()
        label_id = os.getenv("LABEL_ID")
        if label_id is None:
            logger.error("No Label ID found. Unable to process any message.")
            logger.info("Processing ending early.")
            sys.exit(ExitCodes.NO_LABEL_ID)
        else:
            # Build notification credentials dictionary
            notification_credentials = {}
            
            # LINE credentials
            line_token = os.getenv("LINE_TOKEN_PERSONAL")
            if line_token:
                notification_credentials['token'] = line_token
            
            # Pushover credentials
            pushover_user_key = os.getenv("PUSHOVER_USER_KEY")
            pushover_app_token = os.getenv("PUSHOVER_APP_TOKEN")
            if pushover_user_key and pushover_app_token:
                notification_credentials['user_key'] = pushover_user_key
                notification_credentials['app_token'] = pushover_app_token
            
            if not notification_credentials:
                logger.error("No notification credentials found. Unable to send notifications.")
                logger.error("Unable to process messages.")
                logger.info("Processing ending early.")
                sys.exit(ExitCodes.NO_LINE_ACCESS_TOKEN)
            
            process(logger, notification_credentials, label_id, args.suppressed)


def get_persons_name(data: dict) -> Optional[str]:
    """
    This function looks up the preferred name of the person if possible.
    If no match for the name in the lookup table is found. The name in the email
    will be used. if no name is found then None is returned.

    :param data: The data dict returned after the email has been parsed. Should contain \
    a key of 'name'
    :type data: dict
    :returns: The standardized name or the name in the email or None
    """
    name: Optional[str] = None
    aliases: Optional[Dict[str, str]] = config_parser.build_name_lookup(config)
    if aliases:
        name = config_parser.lookup_name(aliases, data.get("name"))
        if name is None and data.get("name") is not None:
            name = data.get("name")
    return name


def post_processing_gmail_labelling(
    logger,
    gmail_resource,
    message_id: str,
    processed_label,
    service,
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
    logger.debug("adding label")
    label.add_label_to_message(gmail_resource, message_id, processed_label)
    if config_parser.should_mail_be_archived(
        config_parser.gmail_archive_setting(config),
        config_parser.service_archive_settings(config, service),
    ):
        label.archive_message(gmail_resource, message_id)


def process_single_email(gmail_resource, message_id, logger) -> dict:
    """
    Process each message and extract which email service sent it as well as the data
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
    if single_email is not None and "subject" in single_email:
        subject: str = single_email.get("subject")
        logger.debug(f"Subject: {subject}")
        sender: str = single_email.get("from")
        logger.debug(f"Sender: {sender}")
        if subject in subjects:
            # workout which notification we are dealing with and use the correct
            # regular expression string
            logger.debug("Subject Passed.")
            key = sender_service_key.get(sender)
            if key is not None and key in config["services"]:
                if "regex" in config["services"][key]:
                    regex: str = config["services"][key].get("regex")
                    email_body = single_email.get_content()
                    data = find_matches(email_body, regex)
                    data["email_service"] = key
                    return data
            else:
                # This needs to be logged. Means failed to match sender.
                logger.warning(
                    f"Failed to process message_id: {message_id} "
                    f"Matched Subject: {subject} "
                    f"Sender not matched: {sender}"
                )
                return data

        # Not an expected subject line. Ignore this email
        logger.info("This is not a notification.")
        logger.info(f"sender: {sender}\n\t")
        logger.info(f"subject: {subject}\n")
        logger.debug(f"contents: {single_email.get_content()}\n")
        logger.debug(f"Data: {data}\n")
    return data


def process(
    logger, notification_credentials: dict, processed_label: str, suppress_notification: bool
) -> None:  # pylint: disable=too-many-branches,too-many-statements
    """
    This is the main function for processing all email messages that match the
    search conditions and sending notifications.
    
    Args:
        logger: Logger instance for logging messages
        notification_credentials: Dictionary containing credentials for notification services
        processed_label: Gmail Internal Label ID to mark processed messages
        suppress_notification: If True, notifications will be suppressed
    """
    logger.info("Looking for email for notification")
    g_search = config_parser.gmail_search_string(config)
    gmail_resource = resource.get_resource(CONFIG_DIR)
    if g_search is None:
        logger.info("Search String is not valid. Unable to get messages.")
        sys.exit(ExitCodes.MISSING_GOOGLE_SEARCH_STRING)
    message_ids = mail.get_message_ids(gmail_resource, g_search)
    if not mail.found_messages(message_ids):
        logger.debug("There were no messages.")
        logger.info("Ending cleanly with no messages to process")
        sys.exit(ExitCodes.OK)
    list_of_message_ids = mail.get_only_message_ids(message_ids)
    logger.debug(f"message_ids:\n\t{list_of_message_ids}\n")
    for message_id in list_of_message_ids:
        processed = False
        data = process_single_email(gmail_resource, message_id, logger)
        logger.debug(data["email_service"].capitalize())
        logger.debug(f"data: {data}\n")
        # Use Environment provided name.
        name: Optional[str] = os.getenv("NAME")
        logger.debug(f"Name: {name}")
        if name is None:
            logger.debug("looking up name")
            name = get_persons_name(data)
            logger.debug(f"lookup Name: {name}")
        notification_message = str(builder.build_message(name, data))
        if notification_message:
            logger.debug(data["email_service"].capitalize())
            if not suppress_notification:
                # Default to LINE notification service
                notification_service = 'line'
                message_service = NotifierFactory.create(notification_service, notification_credentials)
                message_service.send(notification_message)
            else:
                # Suppressing notifications.
                logger.info(
                    f"Message notification for {data['email_service']} has been suppressed."
                )
            processed = True
        else:
            logger.info(f"Email service: {data['email_service']} is not a callable function.")

        if data.get("email_service") is None and data is not None:
            logger.warning("Subject matched but From was not matched")
        elif data.get("email_service") is None and data is None:
            logger.info("Non-Notification email from expected sender")

        if processed:
            post_processing_gmail_labelling(
                logger,
                gmail_resource,
                message_id,
                processed_label,
                data["email_service"],
            )
            # End of the program
    logger.info("Ending cleanly")


if __name__ == "__main__":
    command()
