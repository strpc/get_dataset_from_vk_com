import os
import logging


def setup_logger():
    """
    Setup main logger
    """

    logformat = "%(asctime)s %(levelname)s %(module)s: %(funcName)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(fmt=logformat, datefmt=datefmt))
    root = logging.getLogger()
    root.setLevel(os.environ.get("LOGLEVEL", logging.INFO))
    root.addHandler(handler)
