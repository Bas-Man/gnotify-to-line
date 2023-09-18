from pathlib import Path
from gmail2line.cli import health


def test_check_credentials_json_file():
    config_dir: Path = Path.cwd() / 'tests' / 'toml'
    assert health.check_credentials_json_file(config_dir) == True


def test_check_config_toml_file():
    config_dir: Path = Path.cwd() / 'tests' / 'toml'
    assert health.check_config_toml_file(config_dir) == True


# This must be tested before test_check_line_token_true
# The code in the next function loads the token for the lifetime
# of this test execution
def test_check_line_token_false():
    assert health.check_line_token('LINE_TOKEN_PERSONAL') is False


def test_check_line_token_true():
    from dotenv import load_dotenv

    load_dotenv()
    assert health.check_line_token('LINE_TOKEN_PERSONAL') is True
