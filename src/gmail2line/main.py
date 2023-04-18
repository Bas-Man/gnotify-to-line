""" A program to send notification through LINE based on Email received."""
from pathlib import Path
import sys
import os
import argparse
import glogger
import toml_handler
import base64
import email
from email import parser
from email import policy
import secrets
import gmail
import line
import constants
import patterns
from dotenv import load_dotenv
from typing import Dict, List, Optional
from googleapiclient.errors import HttpError
import message_builder

load_dotenv()

NAME = os.getenv("NAME_1")
LABEL_ID = os.getenv("LABEL_ID")
ACCESS_TOKEN = os.getenv("LINE_TOKEN")

PICKLE = "token.pickle"
CONFIG_DIR = Path.home() / ".config" / "gmail-notify"
TOML_FILE = CONFIG_DIR / "config.toml"


def list_all_labels_and_ids(logger):
    logger.info("Looking up all Labels and IDs")
    service = gmail.get_service(CONFIG_DIR)
    labels = gmail.get_labels(service)
    for label in labels:
      print(f"Label: {label.get('name')} -> ID: {label.get('id')}")
    logger.info("Finished lookup all Labels and IDs")


def lookup_label_id(logger, args):
    logger.info(f"Looking up Label ID for Label: {args.label}")
    service = gmail.get_service(CONFIG_DIR)
    print(f"Looking for label {args.label}")
    labels = gmail.get_labels(service)
    label_id = gmail.get_label_id_from_list(labels, args.label)
    print(f"Id for label: {args.label} -> ID: {label_id}")
    logger.info("Finished looking up Label ID.")

def cli():
    parser = argparse.ArgumentParser()
    parser.add_argument("-l", "--label")
    parser.add_argument("-la", "--label-all", action='store_true')
    args = parser.parse_args()

    logger = glogger.setup_logging(CONFIG_DIR)

    if args.label_all:
        list_all_labels_and_ids(logger)
    elif args.label:
        lookup_label_id(logger, args)
    else:
      print("processing")
      process()


def found_messages(message_ids) -> bool:
    """
    Return a boolean to indicate if any message have been found.
    :param message_ids:
    :rtype: bool
    """
    return bool(message_ids['resultSizeEstimate'])


def get_only_message_ids(message_ids) -> list:
    ids = []
    for message_id in message_ids['messages']:
        ids.append(message_id['id'])
    return ids


def get_message(service, msg_id: str, logger) -> Optional[email.message.EmailMessage]:
    """
    Retrive the email message assicated with the given msg_id
    :param service: Gmail API connection
    :type service: object
    :param msg_id: The id for the requested message.
    :type msg_id: str
    :param logger: Logger to pass information.
    :type logger: object
    :return: The Email message referenced by mss_id
    :rtype: email.message.EmailMessage
    """
    try:
        msg = service.users().messages().get(userId='me',
                                             id=msg_id,
                                             format='raw').execute()
        msg_in_bytes = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
        email_tmp = email.message_from_bytes(msg_in_bytes,
                                             policy=policy.default)
        email_parser = parser.Parser(policy=policy.default)
        resulting_email = email_parser.parsestr(email_tmp.as_string())
        #return resulting_email
    except HttpError as error:
        logger.error(f"Unable to get message for {msg_id} with error {error}")
        return None
    else:
        return resulting_email


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
    :return: The data extracted from the email. Notifier and data.
    :rtype: tuple
    """
    senders, subjects = toml_handler.senders_subjects(toml_handler.load_toml(TOML_FILE))
    data: Dict[str, str] = {}
    single_email = get_message(service, message_id, logger)
    # Check the subject is an expected notification subject line
    subject = single_email.get("subject")
    logger.debug(f"Subject: {subject}")
    sender: str
    if subject in subjects:
        # workout which notification we are dealing with and use the correct
        # regular expression string
        logger.debug(f"Subject Passed.")
        sender = single_email.get("from")
        logger.debug(f"Sender: {sender}")
        email_body = single_email.get_content()
        if sender == constants.FROM_BUS:
            data = patterns.findMatches(email_body,
                                        patterns.BUS_DATA)
            datetime = patterns.findMatches(email_body,
                                            patterns.BUS_DATE_TIME)
            # Merge data and datetime into a single dictionary
            if data is not None:
                data.update(datetime)
                data['notifier'] = "BUS"
        elif sender == constants.FROM_INSTITUTE:
            data = patterns.findMatches(email_body,
                                        patterns.INSTITUTE_DATA)
            data['notifier'] = "INSTITUTE"
        elif sender == constants.FROM_KIDZDUO:
            data = patterns.findMatches(email_body,
                                        patterns.KIDZDUO_ENTEREXIT)
            data['notifier'] = "KIDZDUO"

        elif sender == constants.FROM_GATE:
            data = patterns.findMatches(email_body,
                                        patterns.GATE_DATETIME)
            data['notifier'] = "GATE"

        elif sender == constants.FROM_TRAIN:
            data = patterns.findMatches(email_body, patterns.TRAIN_DATA)
            data['notifier'] = "TRAIN"

        elif sender == constants.FROM_NICHINOKEN:
            data = patterns.findMatches(email_body, patterns.NICHI_DATE)

            data['notifier'] = "NICHINOKEN"
        else:
            # This needs to be logged. Means failed to match sender.
            # if notifier is None:
            logger.warning(f"Failed to process message_id: {message_id} "
                           f"Matched Subject: {subject} "
                           f"Sender not matched: {sender}")
        return data
    # Not an expected subject line. Ignore this email
    logger.info("This is not a notifcation.")
    logger.info(f"sender: {sender}\n\t")
    logger.info(f"subject: {subject}")
    return data


def process():  # pylint: disable=too-many-branches,too-many-statements
    logger = glogger.setup_logging(CONFIG_DIR)
    logger.info("Looking for email for notification")
    service = gmail.get_service(CONFIG_DIR)
    message_ids = gmail.get_message_ids(service, secrets.SEARCH_STRING)
    if not found_messages(message_ids):
        logger.debug("There were no messages.")
        logger.info("Ending cleanly with no messages to process")
        sys.exit(0)
    list_of_message_ids = get_only_message_ids(message_ids)
    logger.debug(f"message_ids:\n\t{list_of_message_ids}\n")
    for message_id in list_of_message_ids:
        processed = False
        data = handle_each_email(service, message_id, logger)
        logger.debug(f"data: {data}\n")
        # Notifier tells us how the data dict is structured
        if data['notifier'] == "BUS":
            logger.debug("Bus")
            message = (f"{NAME} boarded \n"
                       f" the {data['busname']} bound for \n"
                       f"{data['destination']} at stop: {data['stop']}\n"
                       f"at {data['time']} on {data['date']}"
                       )
            line.send_notification(message_builder.bus(NAME, data), ACCESS_TOKEN)
            processed = True
        elif data['notifier'] == "KIDZDUO":
            logger.debug("KidsDuo")
            line.send_notification(message_builder.kidzduo(NAME, data), ACCESS_TOKEN)
            processed = True
        elif data['notifier'] == "GATE":
            logger.debug("Gate")
            line.send_notification(message_builder.gate(NAME, data), ACCESS_TOKEN)
            processed = True
        elif data['notifier'] == "TRAIN":
            logger.debug("Train")
            line.send_notification(message_builder.train(NAME, data), ACCESS_TOKEN)
            processed = True
        elif data['notifier'] == "NICHINOKEN":
            logger.debug("Nichinoken")
            line.send_notification(message_builder.nichinoken(NAME, data), ACCESS_TOKEN)
            processed = True
        elif data['notifier'] == "INSTITUTE":
            logger.debug("Institute")
            line.send_notification(message_builder.institution(NAME, data), ACCESS_TOKEN)
            processed = True
        elif data.get("notifier") is None and data is not None:
            logger.warning("Subject matched but From was not matched")
        elif data.get("notifier") is None and data is None:
            logger.info("Non-Notification email from expected sender")
        else:
            # We should not get here. But log it.
            logger.warning("Something went wrong. Unexpected match. "
                           "Dont know how to handle data."
                           )
        if processed:
            # Mail was processed. Add label so its not processed again
            # Gmail only allows for the shortest time interval of one day.
            logger.debug("adding label")
            gmail.add_label_to_message(
                service, message_id, LABEL_ID)
            # End of the program
    logger.info("Ending cleanly")


if __name__ == '__main__':
    cli()
