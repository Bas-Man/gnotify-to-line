"""
This modules provides functionality to check configuration files can be found.
It also provides a test to check the gmail connection.
"""
import os
from pathlib import Path
import httplib2
from gmail2line.gmail import resource


def check_credentials_json_file(config_dir: Path) -> bool:
    """
    Checks for the existence of the file: credentials.json

    :param config_dir: Configuration directory where the file is expected to be.
    :type config_dir: Path
    :returns: bool
    """
    file_check = config_dir / 'credentials.json'
    return file_check.exists()


def check_config_toml_file(config_dir: Path) -> bool:
    """
    Checks for the existence of the file: config.toml

    :param config_dir: Configuration directory where the file is expected to be.
    :type config_dir: Path
    :returns: bool
    """
    file_check = config_dir / 'config.toml'
    return file_check.exists()


def check_line_token(token_name: str) -> bool:
    """
    This function simply allows you to check that the LINE Token provided can be found in the shell
    environment variable.

    :param token_name: Name of the Token
    :type token_name: str
    :returns: A boolean
    """
    has_token = os.getenv(token_name)
    return has_token is not None


def check_health(config_dir: Path) -> None:
    """
    Runs a series of checks to ensure that the program can connect to gmail.
    Reports and known issues.

    :param config_dir: Path
    :returns: None
    """
    has_errors = False
    print('Checking for file: credentials.json')
    if check_credentials_json_file(config_dir) is False:
        print('Unable to find file: credentials.json')
        has_errors = True
    print('Checking for file: config.toml')
    if check_config_toml_file(config_dir) is False:
        print('Unable to find file: config.tml')
        has_errors = True
    print('Checking Token')
    if not check_line_token('LINE_TOKEN'):
        print('Unable to find LINE_TOKEN')
        has_errors = True
    print('Checking connection to Google.')
    try:
        if resource.get_resource(config_dir) is None:
            print('Unable to connect to Gmail')
            has_errors = True
    except httplib2.ServerNotFoundError as message:
        print(f'{message}')
        print('Check your network settings.')
        has_errors = True
    if has_errors:
        print('Unable to run. Please check the reported errors.')
    else:
        print('All checks PASS!')
