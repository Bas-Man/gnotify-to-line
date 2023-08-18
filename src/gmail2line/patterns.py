# -*- coding: utf-8 -*-
"""
function for handling pattern matching.
"""

import re
from typing import Dict

def findMatches(string, regex) -> Dict[str, str]:
    """
    This is a generic matching function.
    Warning! Your regex expression MUST use 'Named Groups' -> (?P<name>) or \
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
        matches = {}
        for key in match.groupdict():
            matches[key] = match.group(key)
        return matches
    # No Matches
    return {}
