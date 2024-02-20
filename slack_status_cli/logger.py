import logging
import os

DEBUG = bool(os.environ.get("DEBUG", False))


def get_logger(name: str) -> logging.Logger:
    """
    Prepares a standardized logger with the given name.
    """
    logging.basicConfig()
    logger = logging.getLogger(name)
    logger.propagate = False
    logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
    log_handler = logging.StreamHandler()
    log_handler.setLevel(level=logging.DEBUG if DEBUG else logging.INFO)
    log_handler.setFormatter(logging.Formatter(fmt="%(message)s"))
    logger.addHandler(log_handler)

    return logger
