import pickle
import os.path
import sys
import logging
from logging.handlers import RotatingFileHandler
import base64
import email
from email import parser
from email import policy
import secrets
import patterns
import constants
from line_notify import LineNotify
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

ACCESS_TOKEN = secrets.LINE_TOKEN
LOG_FILE = "gnotifier.log"


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify',
          'https://www.googleapis.com/auth/gmail.labels']


def setup_logging():
    """ Setup logging for applciation."""
    # supress google discovery_cache logging
    # https://github.com/googleapis/google-api-python-client/issues/299
    logging.getLogger('googleapiclient.discovery_cache').setLevel(
        logging.ERROR)
    logger = logging.getLogger("gmail-notifier")
    logging.basicConfig(
        handlers=[RotatingFileHandler(LOG_FILE,
                                      maxBytes=100000,
                                      backupCount=10)],
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s')

    return logger


def send_notification(message):
    """
    Send LINE notification
    :param message: The message to be sent via LINE
    :type: str:
    """
    notice = LineNotify(ACCESS_TOKEN)
    notice.send(message)


def get_service():
    """Connect to the Gmail API."""
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    # Another option to ignore google cache logging issue
    # service = build('gmail', 'v1', credentials=creds, cache_discovery=False)
    service = build('gmail', 'v1', credentials=creds)
    return service

# Gmail Label handling functions


def get_labels(service) -> list:
    """
    Get all gmail labels.
    :param service: Gmail service connection object
    :type list:
    """
    list_of_labels = service.users().labels().list(userId='me').execute()
    return list_of_labels.get('labels')


def add_label_to_message(service, msg_id, label_id):
    """
    Add gmail label to given message.
    :param service: Gmail service connection object
    :type service:
    :param msg_id: message identifier
    :type msg_id: str
    :param label_id: Label to be applied to message
    :type label_id: str
    :return: msg
    """
    msg = service.users().messages().modify(userId='me',
                                            id=msg_id,
                                            body={'removeLabelIds': [],
                                                  'addLabelIds': [label_id]}
                                            ).execute()
    return msg


def define_label(name, mlv="show", llv="labelShow") -> dict:
    """
    Define a new label for gmail.
    :param name: Name of new label
    :type name: str
    :param mlv:
    :type mlv: str
    :param llv:
    :type llv: str
    :return: a new label
    :rtype: dict
    """
    label = {}
    label["messageListVisibility"] = mlv
    label["labelListVisibility"] = llv
    label["name"] = name
    return label


def add_label_to_gmail(service, label) -> dict:
    """ Add new label to gmail system. """
    created_label = service.users().labels().create(userId='me',
                                                    body=label).execute()
    return created_label


def get_new_label_id(new_label) -> str:
    """ obtain new label using id. """
    return new_label.get('id')


def get_folders(service, logger):
    """ Get a list of Gmail folders. """
    # Call the Gmail API
    try:
        results = service.users().labels().list(userId='me').execute()
    except Exception as e:
        logger.error(e)
    labels = results.get('labels', [])

    if not labels:
        logger.info('No labels found.')
    else:
        logger.info('Labels:')
        for label in labels:
            logger.info(label['name'])

# End of Gmail Label functions


def get_message_ids(service, search_string) -> dict:

    search = service.users().messages().list(userId='me',
                                             q=search_string).execute()
    return search


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


def get_message(service, msg_id, logger) -> email.message.EmailMessage:
    try:
        msg = service.users().messages().get(userId='me',
                                             id=msg_id,
                                             format='raw').execute()
        msg_in_bytes = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
        email_tmp = email.message_from_bytes(msg_in_bytes,
                                             policy=policy.default)
        emailParser = parser.Parser(policy=policy.default)
        resulting_email = emailParser.parsestr(email_tmp.as_string())
        return resulting_email
    except (errors.HttpError, error):
        logger.error(f"Unable to get message for {msg_id}")
        return None


def handle_each_email(service, message_id, logger) -> tuple:
    data = notifier = None
    single_email = get_message(service, message_id, logger)
    # Check the subject is an expected notification subject line
    subject = single_email.get("subject")
    if subject in constants.SUBJECTS:
        # workout which notification we are dealing with and use the correct
        # regular expression string
        sender = single_email.get("from")
        email_body = single_email.get_content()
        if sender == constants.FROM_BUS:
            data = patterns.findMatches(email_body,
                                        patterns.BUS_DATA)
            datetime = patterns.findMatches(email_body,
                                            patterns.BUS_DATE_TIME)
            # Merge data and datetime into a single dictionary
            data.update(datetime)
            notifier = "BUS"
        elif sender == constants.FROM_KIDZDUO:
            data = patterns.findMatches(email_body,
                                        patterns.KIDZDUO_ENTEREXIT)
            notifier = "KIDZDUO"
        elif sender == constants.FROM_GATE:
            data = patterns.findMatches(email_body,
                                        patterns.GATE_DATETIME)
            notifier = "GATE"
        elif sender == constants.FROM_TRAIN:
            data = patterns.findMatches(email_body, patterns.TRAIN_DATA)
            notifier = "TRAIN"
        else:
            # This needs to be logged. Means failed to match sender.
            # if notifier is None:
            logger.warning(f"Failed to process message_id: {message_id} "
                           f"Matched Subject: {subject} "
                           f"Sender not matched: {sender}")
        return notifier, data
    # Not an expected subject line. Ignore this email
    logger.info("This is not a notifcation.")
    logger.info(f"sender: {sender}\n\t")
    logger.info(f"subject: {subject}")
    return notifier, data


def main():
    logger = setup_logging()
    logger.info("Looking for email for notification")
    service = get_service()
    message_ids = get_message_ids(service, secrets.SEARCH_STRING)
    if not found_messages(message_ids):
        logger.debug("There were no messages.")
        logger.info("Ending cleanly with no messages to process")
        sys.exit(0)
    list_of_message_ids = get_only_message_ids(message_ids)
    for message_id in list_of_message_ids:
        processed = False
        notifier, data = handle_each_email(service, message_id, logger)
        # Notifier tells us how the data dict is structured
        if notifier == "BUS":
            logger.debug("Bus")
            message = (f"{secrets.NAME} boarded \n"
                       f" the {data['busname']} bound for \n"
                       f"{data['destination']} at stop: {data['stop']}\n"
                       f"at {data['time']} on {data['date']}")
            send_notification(message)
            processed = True
        elif notifier == "KIDZDUO":
            logger.debug("KidsDuo")
            message = (f"{secrets.NAME} KidzDuo notification.\n"
                       f"{data['date']} at {data['time']}\n"
                       f"KidzDuo{data['enterexit']}")
            send_notification(message)
            processed = True
        elif notifier == "GATE":
            logger.debug("Gate")
            message = (f"{secrets.NAME} passed the school gate.\n"
                       f"{data['date']} at {data['time']}"
                       )
            send_notification(message)
            processed = True
        elif notifier == "TRAIN":
            logger.debug("Train")
            if data['enterexit'] == "入場":
                status = "Entered"
            else:
                status = "Exited"

            message = (f"{secrets.NAME} Train Notification.\n"
                       f"{data['date']}"
                       f"{status} {data['station']}"
                       )
            send_notification(message)
            processed = True
        elif notifier is None and data is not None:
            logger.warning("Subject matched but From was not matched")
        elif notifier is None and data is None:
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
            add_label_to_message(
                    service, message_id, secrets.LABEL_ID)
            # End of the program
    logger.info("Ending cleanly")


if __name__ == '__main__':
    main()
