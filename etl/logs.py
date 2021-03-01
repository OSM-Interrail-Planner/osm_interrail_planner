import sys
import os
import logging


def init_logger() -> None:
    """ Initializes the logger

    """
    log_level = logging.INFO
    logging.basicConfig(level=log_level)
    logger = logging.getLogger("gps-logger")
    c_handler = logging.StreamHandler()
    c_handler.setLevel(log_level)
    c_format = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
    c_handler.setFormatter(c_format)
    logger.addHandler(c_handler)
    logger.propagate = False


def die(msg: str) -> None:
    """ Prints messagem `msg` and stops the process with failure

        Args:
            msg (str): the string to be printed.
    """
    logging.getLogger("gps-logger").error(f"{msg}")
    os._exit(0)
    sys.exit(1)


def info(msg: str) -> None:
    """ Prints message `msg` for information purposes

        Args:
            msg (str): the string to be printed
    """
    logging.getLogger("gps-logger").info(f"{msg}")


def done(msg: str) -> None:
    """ Prints message `msg` and stops the process with success

        Args:
            msg (str): the string to be printed
    """
    logging.getLogger("gps-logger").info(f"{msg}")
    sys.exit(0)

