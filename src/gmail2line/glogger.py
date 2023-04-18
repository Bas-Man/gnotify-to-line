from pathlib import Path
from logging.handlers import RotatingFileHandler
import logging

LOG_FILE = "gnotifier.log"

def setup_logging(config_dir: Path):
    """ Setup logging for applciation."""
    # suopress google discovery_cache logging
    # https://github.com/googleapis/google-api-python-client/issues/29
    log_file = config_dir / LOG_FILE
    logging.getLogger('googleapiclient.discovery_cache').setLevel(
        logging.ERROR)
    logger = logging.getLogger("gmail-notifier")
    logging.basicConfig(
        handlers=[RotatingFileHandler(log_file,
                                      maxBytes=100000,
                                      backupCount=10)],
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s')

    return logger
