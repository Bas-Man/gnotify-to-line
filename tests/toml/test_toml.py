from gmail2line import config_parser
from pathlib import Path


def test_none_none():
    assert config_parser.should_mail_be_archived(None, None) == False


def test_none_false():
    assert config_parser.should_mail_be_archived(None, False) == False

def test_none_true():
    assert config_parser.should_mail_be_archived(None, True) == True

def test_false_none():
    assert config_parser.should_mail_be_archived(False, None) == False


def test_false_true():
    assert config_parser.should_mail_be_archived(False, True) == True


def test_false_false():
    assert config_parser.should_mail_be_archived(False, False) == False


def test_true_none():
    assert config_parser.should_mail_be_archived(True, None) == True


def test_true_false():
    assert config_parser.should_mail_be_archived(True, False) == False


def test_true_true():
    assert config_parser.should_mail_be_archived(True, True) == True


def test_my_config_gmail_archive():
    config_path = Path.cwd() / 'tests' / 'toml' / 'gmail_false.toml'
    config = config_parser.load_toml(config_path)
    assert config_parser.gmail_archive_setting(config) is not None
    assert config_parser.gmail_archive_setting(config) == False


def test_gmail_true_from_config():
    config_path = Path.cwd() / 'tests' / 'toml' / 'gmail_true.toml'
    config = config_parser.load_toml(config_path)
    assert config_parser.gmail_archive_setting(config) is not None
    assert config_parser.gmail_archive_setting(config) is True
    assert (
        config_parser.should_mail_be_archived(
            config_parser.gmail_archive_setting(config), None
        )
        == True
    )


def test_service_archive_settings_bus_true():
    config_path = Path.cwd() / 'tests' / 'toml' / 'config.toml'
    config = config_parser.load_toml(config_path)
    assert config_parser.service_archive_settings(config, 'bus') == True


def test_service_archive_settings_train_none():
    config_path = Path.cwd() / 'tests' / 'toml' / 'config.toml'
    config = config_parser.load_toml(config_path)
    assert config_parser.service_archive_settings(config, 'train') == None


def test_service_archive_settings_tokyoinstitute_false():
    config_path = Path.cwd() / 'tests' / 'toml' / 'config.toml'
    config = config_parser.load_toml(config_path)
    assert (
        config_parser.service_archive_settings(config, 'tokyoinstitute')
        == False
    )


def test_people():
    config_path = Path.cwd() / 'tests' / 'toml' / 'config.toml'
    config = config_parser.load_toml(config_path)
    names = config_parser.build_name_lookup(config)
    assert names is not None
    assert 'Tamao' == config_parser.lookup_name(names, 'ｽﾊﾟﾝ ﾀﾏｵ ｱｲﾋﾞｰﾛｰｽﾞ')
    assert 'Bob' == config_parser.lookup_name(names, 'billy bob')
    assert config_parser.lookup_name(names, 'bogus') is None
