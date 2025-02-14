"""
This module handles labeling issues with Gmail.
"""
from typing import Dict, List, Optional
from googleapiclient.errors import HttpError


def get_labels(gmail_resource) -> List[Dict[str, str]]:
    """
    Get all gmail labels.

    :param gmail_resource: Gmail service connection object
    :type gmail_resource: Object
    :return: List of Gmail Labels
    :rtype: List[Dict[str,str]]
    """
    list_of_labels = (
        gmail_resource.users().labels().list(userId='me').execute()
    )
    return list_of_labels.get('labels')


def setup_new_label(gmail_resource) -> None:
    """
    This function takes you through the process of creating and setting
    up a new label with Gmail.
    :param gmail_resource: Gmail Service connection
    :returns: None
    """
    label_name: str = input('Enter new Label Name: ').strip()
    # Check that label does not already exist. If it does. Return the label ID
    # If it does not exist. Create the new label and register it with Gmail and
    #  return the newly create ID.
    print(f'Checking if {label_name} is already registered with account.')
    list_of_labels = get_labels(gmail_resource)
    label_id = get_label_id_from_list(list_of_labels, label_name)
    if label_id is not None:
        print('Label already registered in Gmail.')
        print(f'Label: {label_name} -> Label ID: {label_id}')
    else:
        print('No label registered in Gmail.')
        print('Creating new label request.')
        new_label = define_label(label_name)
        print(f'Registering Label: {label_name} with Gmail.')
        registered_label = register_label_with_gmail(gmail_resource, new_label)
        print('New label registered.')
        print(
            f'Label: {label_name} has Gmail ID: {get_label_id(registered_label)}'
        )


def update_messsage_labels(
    gmail_resource,
    msg_id: str,
    add_labels: Optional[List[str]] = None,
    remove_labels: Optional[List[str]] = None,
) -> str:
    """
    Convinence method to allow you to add and or remove multiple labels in a single call.

    :param gmail_resource: Gmail service connection object
    :type gmail_resource:
    :param msg_id: message identifier
    :type msg_id: str
    :param add_labes: A list of labels to be added to the msg_id
    :type add_label: List[str]
    :param remove_labels: A list of labels to be removed from the msg_id
    :type remove_labels: List[str]
    :returns: msg:
    :rtype: str
    """

    if add_labels is None:
        add_labels = []
    if remove_labels is None:
        remove_labels = []

    msg = (
        gmail_resource.users()
        .messages()
        .modify(
            userId='me',
            id=msg_id,
            body={'removeLabelIds': remove_labels, 'addLabelIds': add_labels},
        )
        .execute()
    )
    return msg


def add_label_to_message(gmail_resource, msg_id: str, label_id: str) -> str:
    """
    Add the provided label ID string to the Gmail message.

    :param gmail_resource: Gmail service connection object
    :type gmail_resource:
    :param msg_id: message identifier
    :type msg_id: str
    :param label_id: Label to be applied to message
    :type label_id: str
    :returns: msg:
    :rtype: str
    """
    msg = (
        gmail_resource.users()
        .messages()
        .modify(
            userId='me',
            id=msg_id,
            body={'removeLabelIds': [], 'addLabelIds': [label_id]},
        )
        .execute()
    )
    return msg


def archive_message(gmail_resource, msg_id) -> str:
    """
    Remove the 'INBOX' label from the provided message identifier

    :param gmail_resource: Gmail service connection object
    :type gmail_resource:
    :param msg_id: message identifier
    :type msg_id: str
    :returns: msg
    """
    msg = (
        gmail_resource.users()
        .messages()
        .modify(
            userId='me',
            id=msg_id,
            body={'removeLabelIds': ['INBOX'], 'addLabelIds': []},
        )
        .execute()
    )
    return msg


def list_all_labels_and_ids(gmail_resource, logger) -> None:
    """
    Displays all Gmail Labels found.

    :rtype: None
    """
    logger.info('Looking up all Labels and IDs')
    labels = get_labels(gmail_resource)
    for label in labels:
        print(f"Label: {label.get('name')} -> ID: {label.get('id')}")
    logger.info('Finished lookup all Labels and IDs')


def lookup_label_id(gmail_resource, logger, args) -> None:
    """
    Look up the Internal Gmail ID label for the user defined label provided.

    :rtype: None
    """
    logger.info(f'Looking up Label ID for Label: {args.label}')
    print(f'Looking for label {args.label}')
    labels = get_labels(gmail_resource)
    label_id = get_label_id_from_list(labels, args.label)
    print(f'ID for label: {args.label} -> ID: {label_id}')
    logger.info('Finished looking up Label ID.')


def define_label(name: str, mlv: str = 'show', llv: str = 'labelShow') -> dict:
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
    label['messageListVisibility'] = mlv
    label['labelListVisibility'] = llv
    label['name'] = name
    return label


def register_label_with_gmail(gmail_resource, label) -> dict:
    """
    Register the provide label with the gmail system.

    :param gmail_resource: The gmail service
    :type gmail_resource: object
    :param label: Label to be registered
    :type label: dict
    :returns: The label and associated details from gmail.
    :rtype: dict
    """
    created_label = (
        gmail_resource.users()
        .labels()
        .create(userId='me', body=label)
        .execute()
    )
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


def get_folders(gmail_resource, logger):
    """
    Document me
    """
    # Call the Gmail API
    try:
        results = gmail_resource.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            logger.info('No labels found.')
        else:
            logger.info('Labels:')
            for label in labels:
                logger.info(label['name'])

    except HttpError as err:
        logger.error(err)
