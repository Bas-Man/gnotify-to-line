"""
Exit Codes: Just a convenience module
"""

from enum import IntEnum

class ExitCodes(IntEnum):
    """
    Just a convenience way to document exit codes.
    """

    OK = 1
    """ Everything went ok. """

    MISSING_GOOGLE_SEARCH_STRING = 50
    "There is no Google Search String. Can not filter mail messages for processing."

    INVALID_SENDER = 55
    "The sender address is not valid."

    INVALID_SUBJECT = 60
    "The subject string is not valid."

    NO_LABEL_ID = 65
    "No Email Label Detected."

    NO_LINE_ACCESS_TOKEN = 70
    "No LINE ACCESS Token provided."
