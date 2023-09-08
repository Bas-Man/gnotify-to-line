from pathlib import Path
from gmail2line import health

def test_check_credentials_json_file():
    config_dir: Path = Path.cwd() / "tests" / "toml"
    assert health.check_credentials_json_file(config_dir) == True


def test_check_config_toml_file():
    config_dir: Path = Path.cwd() / "tests" / "toml"
    assert health.check_config_toml_file(config_dir) == True
