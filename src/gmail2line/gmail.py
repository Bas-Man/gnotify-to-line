"""
Document me
"""
import pickle
from pathlib import Path
from typing import Dict, List, Optional
import base64
import email
from email import parser
from email import policy
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

PICKLE = "token.pickle"

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify',
          'https://www.googleapis.com/auth/gmail.labels']

def get_service(config_dir: Path):
    """
    Connect to the Gmail API.

    :return: Return a connection to the Google API Service.
    :rtype object:
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    pickle_file = get_valid_path(config_dir, PICKLE)
    credentials_json = get_valid_path(config_dir, '.credentials.json')
    if pickle_file is not None:
        with pickle_file.open("rb") as f:
            creds = pickle.load(f)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # I suspect that 'credentials_json' needs to be converted from \
            # Path to str to work correctly?
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_json, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        # If there is no pickle file we store it in the .config/app directory
        if pickle_file is None:
            pickle_file = config_dir / PICKLE
        with pickle_file.open('wb') as token:
            pickle.dump(creds, token)
    # Another option to ignore google cache logging issue
    # return build('gmail', 'v1', credentials=creds, cache_discovery=False)
    return build('gmail', 'v1', credentials=creds)

def get_valid_path(config_dir: Path, filename: str) -> Optional[Path]:
    """
    Looks in the current working directory and the `config_dir` to find the provided
    filename. Returns the first valid path found.

    :param config_dir: Provided configuration directory.
    :type config_dir: Path
    :param filename: Name of the file to check for.
    :type filename: str
    :return: Returns the path found if it exists or None if no filename.
    :rtype: Optional[Path]
    """
    # Check if file exists in the current directory
    current_dir_path = Path.cwd() / filename
    if current_dir_path.exists():
        return current_dir_path

    # Check if file exists in ~/.config/somedir/
    config_path = config_dir / filename
    if config_path.exists():
        return config_path

    # If file is not found, return None
    return None

def get_only_message_ids(message_ids) -> list:
    """
    Document me
    """
    ids = []
    for message_id in message_ids['messages']:
        ids.append(message_id['id'])
    return ids


def get_labels(service) -> List[Dict[str,str]]:
    """
    Get all gmail labels.

    :param service: Gmail service connection object
    :type service: Object
    :return: List of Gmail Labels
    :rtype: List[Dict[str,str]]
    """
    list_of_labels = service.users().labels().list(userId='me').execute()
    return list_of_labels.get('labels')


def add_label_to_message(service, msg_id: str, label_id: str) -> str:
    """
    Add gmail label to given message.

    :param service: Gmail service connection object
    :type service:
    :param msg_id: message identifier
    :type msg_id: str
    :param label_id: Label to be applied to message
    :type label_id: str
    :returns: msg:
    :rtype: str
    """
    msg = service.users().messages().modify(userId='me',
                                            id=msg_id,
                                            body={'removeLabelIds': [],
                                                  'addLabelIds': [label_id]}
                                            ).execute()
    return msg

def list_all_labels_and_ids(config_dir, logger) -> None:
    """
    Displays all Gmail Labels found.

    :rtype: None
    """
    logger.info("Looking up all Labels and IDs")
    service = get_service(config_dir)
    labels = get_labels(service)
    for label in labels:
        print(f"Label: {label.get('name')} -> ID: {label.get('id')}")
    logger.info("Finished lookup all Labels and IDs")

def lookup_label_id(config_dir, logger, args) -> None:
    """
    Look up the Internal Gmail ID label for the user defined label provided.

    :rtype: None
    """
    logger.info(f"Looking up Label ID for Label: {args.label}")
    service = get_service(config_dir)
    print(f"Looking for label {args.label}")
    labels = get_labels(service)
    label_id = get_label_id_from_list(labels, args.label)
    print(f"ID for label: {args.label} -> ID: {label_id}")
    logger.info("Finished looking up Label ID.")

def archive_message(service, msg_id) -> str:
    """
    Remove the 'INBOX' label from the provided message identifier

    :param service: Gmail service connection object
    :type service:
    :param msg_id: message identifier
    :type msg_id: str
    :returns: msg
    """
    msg = service.users().messages().modify(userId='me',
                                            id=msg_id,
                                            body={'removeLabelIds': ['INBOX'],
                                                  'addLabelIds': []}
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
    :returns: a new label
    :rtype: dict
    """
    label = {}
    label["messageListVisibility"] = mlv
    label["labelListVisibility"] = llv
    label["name"] = name
    return label


def register_label_with_gmail(service, label) -> dict:
    """
    Register the provide label with the gmail system.

    :param service: The gmail service
    :type service: object
    :param label: Label to be registered
    :type label: dict
    :returns: The label and associated details from gmail.
    :rtype: dict
    """
    created_label = service.users().labels().create(userId='me',
                                                    body=label).execute()
    return created_label


def get_label_id(label) -> str:
    """
    Obtain new label using ID.

    :param label: Gmail label
    :type label: dict
    :returns: The ID of the label passed in to the function
    :rtype: str
    """
    return label.get('id')

def get_label_id_from_list(list_of_labels: List, name: str) -> Optional[str]:
    """
    Document me
    """
    for label in list_of_labels:
        if label['name'] == name:
            return label['id']
    return None

def get_folders(service, logger):
    """
    Document me
    """
    # Call the Gmail API
    try:
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            logger.info('No labels found.')
        else:
            logger.info('Labels:')
            for label in labels:
                logger.info(label['name'])

    except HttpError as e:
        logger.error(e)


def get_message_ids(service, search_string: str) -> dict:
    """
    Searchs Gmail for any messages that match the search string provided.

    :param service: The Gmail API connection.
    :type service: object
    :param search_string: The Gmail search string to use.
    :type search_string: str
    :returns: A dictionary of messages that match the search string.
    :rytpe: dict
    """
    message_ids = service.users().messages().list(userId='me',
                                                  q=search_string).execute()
    return message_ids

def get_message(service, msg_id: str, logger) -> Optional[email.message.EmailMessage]:
    """
    Retrive the email message assicated with the given msg_id

    :param service: Gmail API connection
    :type service: object
    :param msg_id: The id for the requested message.
    :type msg_id: str
    :param logger: Logger to pass information.
    :type logger: object
    :returns: The Email message referenced by mss_id
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
    except HttpError as error:
        logger.error(f"Unable to get message for {msg_id} with error {error}")
        return None
    else:
        return resulting_email

def found_messages(message_ids) -> bool:
    """
    Return a boolean to indicate if any message have been found.

    :param message_ids:
    :rtype: bool
    """
    return bool(message_ids['resultSizeEstimate'])
