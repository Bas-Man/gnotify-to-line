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
        with open(config_file, mode='rb') as file:
            config: Dict[str, str] = tomllib.load(file)
    except FileNotFoundError:
        print(f'Config file: {config_file} not found')
        config = {}
    return config


def gmail_search_string(config: Dict) -> Optional[str]:
    """
    Give easy access to the Gmail Search string.
    """
    return config['gmail'].get('search')


def get_valid_path(config_dir: Path, filename: str) -> Optional[Path]:
    """
    Looks in the current working directory and the `config_dir` to find the provided
    filename. Returns the first valid path found.

    :param config_dir: Provided configuration directory.
    :type config_dir: Path
    :param filename: Name of the file to check for.
    :type filename: str
    :returns: Returns the path found if it exists or None if no filename.
    :rtype: Optional[Path]
    """
    # Check if file exists in the current directory
    current_dir_path = Path.cwd() / filename
    if current_dir_path.exists():
        return current_dir_path

    # Check if file exists in ~/.config/somedir/
    config_path = config_dir / filename
    if config_path.exists():
        return config_path

    # If file is not found, return None
    return None


def senders_subjects(
    config: Dict,
) -> Tuple[List[str], List[str], Dict[str, str]]:
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


def build_name_lookup(config: Dict) -> Optional[Dict[str, str]]:
    """
    Document me
    """
    name_lookup_idx: Dict[str, str] = {}
    if 'people' in config:
        for name, name_list in config['people'].items():
            aliases = name_list.get('alias')
            for alias in aliases:
                name_lookup_idx[alias] = name.capitalize()
    return name_lookup_idx


def lookup_name(
    name_lookup_idx: Dict[str, str], alias: Optional[str]
) -> Optional[str]:
    """
    Document me
    """
    if alias is None:
        return None
    return name_lookup_idx.get(alias)


def gmail_archive_setting(config: Dict) -> Optional[bool]:
    """
    This function accesses the [gmail] archive setting.

    :param config: Configuration afte being loaded.
    :type config: dict
    :return: True or False or None if there is not configuration value
    :rtype: Optional[bools]
    """
    return config['gmail'].get('archive')


def service_archive_settings(
    config: Dict, config_service: str
) -> Optional[bool]:
    """
    If the service is defined in the config and has an 'archive' option this value will be returned.

    :param config: reference to the service archive setting.
    :type: dict
    :Returns: None or the value stored in the option.
    :rtype: Optional[bool]
    """
    return config['services'][config_service].get('archive')


def should_mail_be_archived(
    global_config: Optional[bool], sender_config: Optional[bool]
) -> bool:
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

    path = Path.home() / '.config' / 'gmail-notify' / 'config.toml'
    options = load_toml(path)
    print('All Data')
    pprint(options)

    gsearch = gmail_search_string(options)
    print('GSearch')
    pprint(gsearch)
    senders, subjects, sender_key = senders_subjects(options)
    pprint(senders)
    print('\n')
    pprint(subjects)
    print('\n')
    pprint(sender_key)
