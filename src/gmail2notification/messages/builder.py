"""
Module of common message building functions
"""
from typing import Optional

from gmail2notification.messages.japan import (
    nichinoken,
    bus,
    train,
    tokyoinstitute,
    gate,
    kidzduo,
)


def build_message(name: Optional[str], data: dict) -> Optional[object]:
    """
    Based on the value of the `key` 'email_service' the correct message building function
    is called.

    :param name: Name of the person who triggered the notification.
    :type name: Optional[str]
    :param data: A dictionary contain the information extracted from the email.
    :type data: dict
    :returns: This returns None if the email service is not supported or the formatted string.
    :rtype: Optional[object]
    """
    func = globals().get(data['email_service'])
    if callable(func):
        return func(name, data)
    return None
