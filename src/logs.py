import logging
import os.path
from Utils import Utils
from datetime import datetime

config = Utils().get_config()['LOG']

CRITICAL = logging.CRITICAL
ERROR = logging.ERROR
WARN = logging.WARN
INFO = logging.INFO
DEBUG = logging.DEBUG

LOGGING_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DIR = os.path.join( os.path.dirname(os.path.realpath(__file__)), config['LOG_REL_PATH'].replace("'", ""))
LOG_FILE_NAME = config['LOG_FILE_NAME'].replace("'", "")


if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


def critical(log_message):
    logging.critical(log_message)


def error(log_message):
    logging.error(log_message)


def warning(log_message):
    logging.warning(log_message)


def info(log_message):
    logging.info(log_message)


def debug(log_message):
    logging.debug(log_message)


def setup_logger(logger_name='Main', log_format=LOGGING_FORMAT, log_level=DEBUG, log_file_name=LOG_FILE_NAME):
    logging.basicConfig(format=log_format,
                        filename=os.path.join(LOG_DIR, log_file_name.format(date=datetime.now().strftime('%d_%m_%y'))),
                        level=log_level,
                        datefmt='%m/%d/%Y %I:%M:%S %p')

    return logging.getLogger(name=str(logger_name))


def disable_logger():
    logging.shutdown()
