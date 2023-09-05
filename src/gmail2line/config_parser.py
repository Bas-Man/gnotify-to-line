# -*- coding: utf-8 -*-
"""
This module provides functions for dealing with the config.toml file.
"""
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


def load_toml(config_file: Path) -> Dict[str, Any]:
    """
    Load the configuration file
    """
    try:
        with open(config_file, mode="rb") as fp:
            config: Dict[str, str] = tomllib.load(fp)
    except FileNotFoundError:
        print(f"Config file: {config_file} not found")
        config = {}
    return config

def gmail_search_string(config: Dict) -> Optional[str]:
    """
    Give easy access to the Gmail Search string.
    """
    return config['gmail'].get('search')


def senders_subjects(config: Dict) -> Tuple[List[str], List[str], Dict[str, str]]:
    """
    Docuemnt me
    """
    subjects: List[str] = []
    senders: List[str] = []
    sender_as_key: Dict[str, str] = {}
    for service_name, service_data in config['services'].items():
        sender: str = service_data['sender']
        senders.append(sender)
        sender_as_key[sender] = service_name
        if 'subjects' in service_data:
            for subject in service_data['subjects']:
                subjects.append(subject)
    return (senders, subjects, sender_as_key)

def gmail_archive_setting(config: Dict) -> Optional[bool]:
    """
    This function accesses the [gmail] archive setting.

    :param config: Configuration afte being loaded.
    :type config: dict
    :return: True or False or None if there is not configuration value
    :rtype: Optional[bools]
    """
    return config['gmail'].get('archive')

def service_archive_settings(config: Dict, config_service: str) -> Optional[bool]:
    return config['services'][config_service].get('archive')


def should_mail_be_archived(global_config: Optional[bool], sender_config: Optional[bool]) -> bool:
    """
    This function determines if the mail should be removed from the `INBOX` based on the
    configuration settings combining [gmail] and [services.service_name]

    :param global_config:
    :type global_config: Optional[bool]
    :param sender_config:
    :type sender_config: Optional[bool]
    :return: True or False
    :rtype: bool
    """
    if sender_config is True:
        return True
    if global_config is True and sender_config is None:
        return True
    return False

if __name__ == '__main__':
    from pprint import pprint
    path = Path.home() / ".config" / "gmail-notify" / "config.toml"
    options = load_toml(path)
    pprint(options)

    gsearch = gmail_search_string(options)
    pprint(gsearch)
    senders, subjects, sender_key = senders_subjects(options)
    pprint(senders)
    print("\n")
    pprint(subjects)
    print("\n")
    pprint(sender_key)
