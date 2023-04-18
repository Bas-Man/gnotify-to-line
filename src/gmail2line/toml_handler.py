# -*- coding: utf-8 -*-
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def load_toml(config_file: Path) -> Dict[str,str]:
    try:
        with open(config_file, mode="rb") as fp:
            config: Dict[str, str] = tomllib.load(fp)
    except FileNotFoundError:
        print(f"Config file: {config_file} not found")
        config = {}
    return config


def senders_subjects(config) -> Tuple[List[str], List[str]]:
    subjects: List[str] = []
    senders: List[str] = []
    for service_name, service_data in config['services'].items():
        senders.append(service_data['sender'])
        if 'subjects' in service_data:
            for subject in service_data['subjects']:
                subjects.append(subject)
    return (senders,subjects)

if __name__ == '__main__':
    from pprint import pprint
    path = Path.home() / ".config" / "gmail-notify" / "config.toml"
    options = load_toml(path)

    senders, subjects = senders_subjects(options)
    pprint(senders)
    print("\n")
    pprint(subjects)
