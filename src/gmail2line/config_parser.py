# -*- coding: utf-8 -*-
"""
Docment me
"""
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def load_toml(config_file: Path) -> Dict[str,str]:
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

def gmail_search_string(config) -> Optional[str]:
    """
    Give easy access to the Gmail Search string.
    """
    return config['gmail'].get('search')


def senders_subjects(config) -> Tuple[List[str], List[str], Dict[str, str]]:
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

def gmail_archive_setting(config) -> Optional[bool]:
    """
    Document me
    """
    return config['gmail'].get('archive')

def should_mail_be_archived(global_config: Optional[bool], sender_config: Optional[bool]) -> bool:
    """ Document me
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
