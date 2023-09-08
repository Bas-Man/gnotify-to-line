"""
Module for connecting to Gmail Service.
"""
import pickle
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from gmail2line import config_parser

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
    pickle_file = config_parser.get_valid_path(config_dir, PICKLE)
    credentials_json = config_parser.get_valid_path(config_dir, 'credentials.json')
    if pickle_file is not None:
        with pickle_file.open("rb") as file:
            creds = pickle.load(file)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
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
