"""
Exit Codes: Just a convenience module
"""

from enum import IntEnum

class ExitCodes(IntEnum):
    """Document Class"""

    OK = 1
    """ Everything went ok"""

    MISSING_GOOGLE_SEARCH_STRING = 50
    "There is no Google Search String. Can not filter mail messages for processing"

    INVALID_SENDER = 55

    INVALID_SUBJECT = 60

    NO_LABEL_ID = 65

    NO_LINE_ACCESS_TOKEN = 70
