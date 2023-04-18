import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from pathlib import Path
from typing import Dict, List, Optional

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
    if pickle_file is not None:
        with pickle_file.open("rb") as f:
            creds = pickle.load(f)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        # If there is no pickle file we store it in the .config/app directory
        if pickle_file is None:
            pickle_file = config_dir / PICKLE
        with pickle_file.open('wb') as token:
            pickle.dump(creds, token)
    # Another option to ignore google cache logging issue
    # service = build('gmail', 'v1', credentials=creds, cache_discovery=False)
    return build('gmail', 'v1', credentials=creds)

def get_valid_path(config_dir: Path, filename: str) -> Optional[Path]:
    # Check if file exists in the current directory
    current_dir_path = Path.cwd() / filename
    if current_dir_path.exists():
        return current_dir_path

    # Check if file exists in ~/.config/somedir/
    home_dir = Path.home()
    config_path = config_dir / filename
    if config_path.exists():
        return config_path

    # If file is not found, return None
    return None

def get_only_message_ids(message_ids) -> list:
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
    :rtype: list
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


def register_label_with_gmail(service, label) -> dict:
    """
    Register the provide label with the gmail system.
    :param service: The gmail service
    :type service: object
    :param label: Label to be registered
    :type label: dict
    :return: The label and associated details from gmail.
    :rtype: dict
    """
    created_label = service.users().labels().create(userId='me',
                                                    body=label).execute()
    return created_label


def get_label_id(label) -> str:
    """
    obtain new label using id.
    :param label: Gmail label
    :type label: dict
    :return: The id of the label passed in to the function
    :rtype: str
    """
    return label.get('id')

def get_label_id_from_list(list_of_labels: List, name: str) -> Optional[str]:
    for label in list_of_labels:
        if label['name'] == name:
            return label['id']
    return None

def get_folders(service, logger):
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


def get_message_ids(service, search_string) -> dict:
    """
    Searchs Gmail for any messages that match the search string provided.
    :param service: The Gmail API connection.
    :type service: object
    :param search_string: The Gmail search string to use.
    :type search_string: str
    :return: A dictionary of messages that match the search string.
    :rytpe: dict
    """
    message_ids = service.users().messages().list(userId='me',
                                                  q=search_string).execute()
    return message_ids
