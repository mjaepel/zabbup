import logging
import logging.handlers
from modules.config import config
import sys


def GetLogger(name: str = __name__) -> logging.Logger:
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
            "%(asctime)s " + sys.argv[0] + "[%(process)d] - %(levelname)s: %(message)s "
        )
        handler.setFormatter(handler_formatter)

        logger.addHandler(handler)

        logger.setLevel(config.general.loglevel_numeric)

    return logger
