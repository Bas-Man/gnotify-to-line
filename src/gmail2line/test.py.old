import pickle, os.path, sys
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
import email
from email import parser
from email import policy

SEARCH_STRING = "((label:tamao-kidsduo OR label:tamao-pasmo" \
                ") AND -label:notified)" \
                "AND newer_than:1d"

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.modify',
          'https://www.googleapis.com/auth/gmail.labels']


def get_service():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
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


def get_labels(service):
    list_of_labels = service.users().labels().list(userId='me').execute()
    return list_of_labels.get('labels')


def define_label(name, mlv="show", llv="labelShow"):
    label = dict()
    label["messageListVisibility"] = mlv
    label["labelListVisibility"] = llv
    label["name"] = name
    return label


def add_label_to_gmail(service, label):
    try:
        created_label = service.users().labels().create(userId='me',
                                                        body=label).execute()
        return created_label
    except Exception as e:
        logger.error(e)


def get_new_label_id(new_label):
    return new_label.get('id')


def get_message_ids(service, search_string):
    try:
        search = service.users().messages().list(userId='me',
                                                 q=search_string).execute()
    except (errors.HttpError, error):
        logger.warning("Something went wrong with the http request.")
    return search


def get_only_message_ids(message_ids):
    ids = []
    for anId in message_ids['messages']:
        ids.append(anId['id'])
    return ids


MESSAGE_ID = "1775d10a91ba4249"


def get_message(service, msg_id):
    msg = service.users().messages().get(userId='me',
                                         id=msg_id,
                                         format='raw').execute()
    msg_in_bytes = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
    email_tmp = email.message_from_bytes(msg_in_bytes,
                                         policy=policy.default)
    emailParser = parser.Parser(policy=policy.default)
    resulting_email = emailParser.parsestr(email_tmp.as_string())
    return resulting_email


def main():
    service = get_service()


if __name__ == '__main__':
    main()
