import logging

def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:  # Avoid adding multiple handlers to the same logger
        logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter('[%(asctime)s] - [%(levelname)s] - %(message)s'))
        logger.addHandler(ch)
    return logger

logger = get_logger(__name__)