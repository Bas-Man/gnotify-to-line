"""
Document me
"""
import base64
import email
from typing import Optional
from email import parser
from email import policy
from googleapiclient.errors import HttpError


def get_only_message_ids(message_ids) -> list:
    """
    Document me
    """
    ids = []
    for message_id in message_ids['messages']:
        ids.append(message_id['id'])
    return ids


def get_message_ids(gmail_resource, search_string: str) -> dict:
    """
    Searchs Gmail for any messages that match the search string provided.

    :param gmail_resource: The Gmail API connection.
    :type gmail_resource: object
    :param search_string: The Gmail search string to use.
    :type search_string: str
    :returns: A dictionary of messages that match the search string.
    :rytpe: dict
    """
    message_ids = (
        gmail_resource.users()
        .messages()
        .list(userId='me', q=search_string)
        .execute()
    )
    return message_ids


def get_message(
    gmail_resource, msg_id: str, logger
) -> Optional[email.message.EmailMessage]:
    """
    Retrive the email message assicated with the given msg_id

    :param gmail_resource: Gmail API connection
    :type gmail_resource: object
    :param msg_id: The id for the requested message.
    :type msg_id: str
    :param logger: Logger to pass information.
    :type logger: object
    :returns: The Email message referenced by mss_id
    :rtype: email.message.EmailMessage
    """
    try:
        msg = (
            gmail_resource.users()
            .messages()
            .get(userId='me', id=msg_id, format='raw')
            .execute()
        )
        msg_in_bytes = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))
        email_tmp = email.message_from_bytes(
            msg_in_bytes, policy=policy.default
        )
        email_parser = parser.Parser(policy=policy.default)
        resulting_email = email_parser.parsestr(email_tmp.as_string())
    except HttpError as error:
        logger.error(f'Unable to get message for {msg_id} with error {error}')
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
