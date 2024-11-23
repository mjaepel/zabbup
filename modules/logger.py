import logging
import logging.handlers
import sys


def get_logger(name: str = __name__) -> logging.Logger:
    """Returns a logger instance

    # LOGGER.info('this is info')
    # LOGGER.debug('this is debug')
    # LOGGER.critical('this is critical')

    Logging Level
        debug = 10
        info = 20
        warning = 30
        error = 40
        critical = 50
    """

    logger: logging.Logger = logging.getLogger(name)

    if not len(logger.handlers):
        handler: logging.StreamHandler = logging.StreamHandler(sys.stdout)
        handler_formatter: logging.Formatter = logging.Formatter(
            "%(asctime)s " + sys.argv[0] + "[%(process)d] - %(levelname)s: %(message)s ",
        )
        handler.setFormatter(handler_formatter)

        logger.addHandler(handler)

        logger.setLevel(logging.INFO)

    return logger


def set_log_level(log_level: int) -> None:
    logger = get_logger()
    logger.setLevel(log_level)

    for handler in logger.handlers:
        handler.setLevel(log_level)
