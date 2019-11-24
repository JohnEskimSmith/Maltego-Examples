import sys
import transforms
import logging
from logging.handlers import RotatingFileHandler
from maltego_trx.registry import register_transform_function, register_transform_classes
from maltego_trx.server import app, application
from maltego_trx.handler import handle_run


def project_logs():
    logger = logging.getLogger('project')
    logger.setLevel(logging.INFO)
    log_format = '%(asctime)s - %(levelname)s - %(message)s'
    formatter = logging.Formatter(log_format)
    file_handler = logging.handlers.RotatingFileHandler(LOG_FILE, maxBytes=1024 * 1024 * 10, backupCount=3)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    file_handler_error = logging.handlers.RotatingFileHandler(LOG_FILE_ERRORS, maxBytes=1024 * 1024 * 10, backupCount=1)
    file_handler_error.setLevel(logging.ERROR)
    file_handler_error.setFormatter(formatter)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(file_handler_error)
    return logger
# register_transform_function(transform_func)

LOG_FILE = "project.log"
LOG_FILE_ERRORS = "project.log"
logger = project_logs()
register_transform_classes(transforms)
logger.info(sys.argv)

handle_run(__name__, sys.argv, app)