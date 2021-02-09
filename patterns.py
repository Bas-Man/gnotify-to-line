# -*- coding: utf-8 -*-
"""
"""

import re

# KidzDuo
KIDZDUO_ENTEREXIT = (
    r"""(?P<date>(?:\d{4}(?:[一-龯]|-)\d{2}"""
    r"""(?:[一-龯]|[-])\d{2}[一-龯]?))\s{1,2}(?P<time>\d{2}(?:[一-龯]|:)"""
    r"""\d{2}(?:[一-龯]|[:])\d{2}(?:[一-龯]|))\s"""
    r"""(?P<enterexit>(?:に入室しました)|(?:に退室しました))?"""
    )


# Bus
BUS_DATA = (
    r"^「(?P<busname>[一-龯]\d{1,2})\s(?P<destination>[一-龯]+)行き・"
    r"(?P<stop>[一-龯]+)」"
    )
BUS_DATE_TIME = (
    r"(?P<date>(?:\d{2}(?:[一-龯])\d{2})(?:[一-龯]))\s(?P<time>"
    r"(?:\d{2}(?:[一-龯])\d{2})(?:[一-龯]))"
    )
# Bus and Gate Date and time
GATE_DATETIME = (
    r"(?P<date>(?:\d{4}(?:[一-龯]|-)\d{2}(?:[一-龯]|[-])\d{2}[一-龯]?))\s{1,2}"
    r"(?P<time>\d{2}(?:[一-龯]|:)\d{2}(?:[一-龯]|[:])\d{2}(?:[一-龯]|))"
    )


def findMatches(string, regex) -> dict:
    """
    This is a generic matching function.
    Warning! Your regex expression MUST use 'Named Groups' -> (:P<name>) or \
    this function will return an empty dictionary

    :param string: The text you are searching
    :type string: str
    :param regex: The regular expression string you are using to search
    :type regex: str
    :returns: A dictionary of named key/value pairs. The key value is derived \
    from (?P<name>)
    :returns: None is returned if No match is found.
    :rtype: dict
    :rtype: None
    """
    match = re.search(regex, string, re.UNICODE | re.MULTILINE)
    if match:
        matches = dict()
        for key in match.groupdict():
            matches[key] = match.group(key)
        return matches
    # No Matches
    return None
