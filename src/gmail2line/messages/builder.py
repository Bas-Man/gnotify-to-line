"""
Module of common message building functions
"""
from typing import Optional
from gmail2line.messages.japan import (
    nichinoken,
    bus,
    train,
    tokyoinstitute,
    gate,
    kidzduo,
)


def build_message(name: Optional[str], data: dict) -> Optional[str]:
    """
    Based on the value of the `key` 'notifier' the correct message building function
    is called.

    :param name: Name of the person who triggered the notification.
    :type name: Optional[str]
    :param data: A dictionary contain the information extracted from the email.
    :type data: dict
    :returns: This returns None if the notifier is not supported or the formatted string.
    :rtype: Optional[str]
    """
    func = globals().get(data['notifier'])
    if callable(func):
        return func(name, data)
    return None
