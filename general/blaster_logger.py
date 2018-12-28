import logging
import os
import time
from functools import wraps
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler

LOG_DIR = "YOUR LOG DIR IMPORT HERE"

full_logfile = os.path.join(LOG_DIR, "full.log")
logfile = os.path.join(LOG_DIR, "main.log")
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

fh.setFormatter(file_formatter)
ch.setFormatter(console_formatter)
fh2.setFormatter(file_formatter)
error_log.setFormatter(file_formatter)

logging.basicConfig(level=logging.DEBUG, handlers=[fh, ch, fh2, error_log])

logger = logging.getLogger("BOT")


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
        if execution_time > 3 < 10:
            logger.info(
                f"Execution time: {execution_time} [{func.__module__}.{func.__name__}]"
            )
        elif execution_time >= 10:
            logger.warning(f"Long execution time: {execution_time} [{func.__module__}.{func.__name__}]")

        else:
            logger.debug(
                f"Execution time: {round(end_time - start_time, 4)} [{func.__module__}.{func.__name__}]"
            )
        logger.debug(f"Result {func.__name__}: {log_result} [{func.__module__}]")
        logger.debug(f"Exit: {func.__name__} [{func.__module__}]")
        return result

    return decorator


def log_this_console(func):
    @wraps(func)
    def decorator(*args, **kwargs):
        logger.info(f"Enter: {func.__name__} [{func.__module__}]")
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        logger.info(
            f"Execution time: {round(end_time - start_time, 4)} [{func.__module__}.{func.__name__}]"
        )
        logger.info(f"Result {func.__name__}: {result} [{func.__module__}]")
        logger.info(f"Exit: {func.__name__} [{func.__module__}]")
        return result

    return decorator
