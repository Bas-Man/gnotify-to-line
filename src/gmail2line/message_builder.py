# -*- coding: utf-8 -*-
"""
This module contains functions for building message strings based on the contents of `data`
"""
from typing import Optional

def call_function(name: Optional[str], data: dict) -> Optional[str]:
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

def nichinoken(name: Optional[str], data: dict) -> str:
    """
    This function builds the message string for a notification from Nichinoken.

    :returns: Nichinoken message string.
    :rtype: str
    """
    return (
        f"Nichinoken Notification"
        f"""{f" for {name}" if name is not None else ""}.\n"""
        f"{data['date']} at {data['time']}"
           )

def train(name: Optional[str], data: dict) -> str:
    """
    This function builds the message string for a notification from a train service

    :returns: Train notification message string
    :rtype: str
    """
    if data['enterexit'] == "入場":
        status = "Entered"
    else:
        status = "Exited"
    return (
        f"Train Notification"
        f"""{f" for {name}" if name is not None else ""}.\n"""
        f"{data['date']} at {data['time']}\n"
        f"{status} {data['station']}"
           )

def bus(name: Optional[str], data: dict) -> str:
    """
    This function builds the message string for a bus notification.

    :return: Bus notification message string.
    :rtype: str
    """
    return (f"{name} boarded \n"
            f" the {data['busname']} bound for \n"
            f"{data['destination']} at stop: {data['stop']}\n"
            f"at {data['time']} on {data['date']}"
            )

def gate(name: Optional[str], data: dict) -> str:
    """
    This message builds a notification from the School gate.

    :return: School Gate notification message string
    :rtype: str
    """
    return (f"{name} passed the school gate.\n"
            f"{data['date']} at {data['time']}"
            )

def kidzduo(name: Optional[str], data: dict) -> str:
    """
    This function builds a notification message for KidsDuo

    :return: KidzDuo notification message string
    :rtype: str
    """
    return (
        f"KidzDuo Notification"
        f"""{f" for {name}" if name is not None else ""}.\n"""
        f"{data['date']} at {data['time']}\n"
        f"KidzDuo{data['enterexit']}"
            )

def tokyoinstitute(name: Optional[str], data: dict) -> str:
    """
    Tokyo Institution

    :return: Tokyo Institution notification message string
    :rtype: str
    """
    return (
        f"{data['location']} Notification"
        f"""{f" for {name}" if name is not None else ""}.\n"""
        f"{data['date']} {data['enterexit']}"
            )
