from line_notify import LineNotify
import os

def send_notification(message: str, token) -> None:
    """
    Send LINE notification
    :param message: The message to be sent via LINE
    :type message: str
    """
    notice = LineNotify(token)
    notice.send(message)
