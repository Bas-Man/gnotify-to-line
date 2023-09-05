"""
Logging module simplifies setting up the logger.
"""
from pathlib import Path
from logging.handlers import RotatingFileHandler
import logging

LOG_FILE = "gnotifier.log"

def setup_logging(config_dir: Path, level: str):
    """
    Setup logging for applciation.

    :param config_dir: Path to the config directory where the log will also be written.
    :type config_dir: Path
    :param level: The Level that logger should run at. Values can be \
    INFO, WARN, DEBUG
    :type level: str
    :returns: An instance of logger.
    """
    # suopress google discovery_cache logging
    # https://github.com/googleapis/google-api-python-client/issues/29
    log_file = config_dir / LOG_FILE
    logging.getLogger('googleapiclient.discovery_cache').setLevel(
        logging.ERROR)
    logger = logging.getLogger("gmail-notifier")
    level = logging.getLevelName(level)
    logging.basicConfig(
        handlers=[RotatingFileHandler(log_file,
                                      maxBytes=100000,
                                      backupCount=10)],
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s')

    return logger
