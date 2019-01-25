import logging
import os
import time
from functools import wraps
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

from definitions import LOG_DIR  # Required for logger to work


def make_logger(log_dir):
    full_logfile = os.path.join(log_dir, "full.log")
    logfile = os.path.join(log_dir, "main.log")
    file_formatter = logging.Formatter(
        "%(levelname)-8s %(message)-4s  [%(name)s] [%(filename)s.%(funcName)s] [%(asctime)s]"
    )

    console_formatter = logging.Formatter(
        "%(levelname)-8s %(message)-8s  [%(filename)s] [%(asctime)s]"
    )

    fh = RotatingFileHandler(
        full_logfile,
        mode="a",
        maxBytes=2 * 1024 * 1024,
        backupCount=100,
        encoding="UTF-8",
        delay=False,
    )

    fh2 = TimedRotatingFileHandler(
        logfile, when="midnight", interval=24, backupCount=7, encoding="UTF-8"
    )

    error_log = TimedRotatingFileHandler(
        os.path.join(LOG_DIR, "errors.log"),
        when="midnight",
        interval=24,
        backupCount=60,
        encoding="UTF-8",
    )

    fh2.setLevel(logging.INFO)
    fh.setLevel(logging.DEBUG)
    error_log.setLevel(logging.ERROR)

    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    if os.environ.get('DEBUG'):
        ch.setLevel(logging.DEBUG)

    fh.setFormatter(file_formatter)
    ch.setFormatter(console_formatter)
    fh2.setFormatter(file_formatter)
    error_log.setFormatter(file_formatter)

    logging.basicConfig(level=logging.DEBUG, handlers=[fh, ch, fh2, error_log])

    return logging.getLogger("MAIN")


logger = make_logger(LOG_DIR)
if os.environ.get('DEBUG'):
    logger.warning('DEBUG MODE ON. ALL MESSAGES WILL BE PRINTED TO CONSOLE.')


def log_this(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        logger.debug(f"Enter: {func.__name__} [{func.__module__}]")
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = round(end_time - start_time, 4)
        if isinstance(result, str):
            log_result = result.split("\n")[0]
        else:
            log_result = result

        if execution_time >= 10:
            logger.warning(f"Long execution time: {execution_time} [{func.__module__}.{func.__name__}]")

        logger.debug(f"Execution time: {execution_time}s. Result: {func.__name__}: {log_result} [{func.__module__}]")
        logger.debug(f"Exit: {func.__name__} [{func.__module__}]")
        return result

    return decorator
