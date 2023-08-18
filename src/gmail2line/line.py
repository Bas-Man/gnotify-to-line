"""
Simple module to make using LineNotify package easier
"""
from line_notify import LineNotify

def send_notification(message: str, token: str) -> None:
    """
    Send LINE notification
    :param message: The message to be sent via LINE
    :type message: str
    :param token: Line Access Token
    :type token: str
    """
    notice = LineNotify(token)
    notice.send(message)
