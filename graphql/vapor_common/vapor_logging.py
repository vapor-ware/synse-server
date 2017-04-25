#!/usr/bin/env python
"""
   Vapor CORE Logging Helpers
   Author:  andrew
   Date:    12/7/2015

        \\//
         \/apor IO
"""
import logging
import logging.config
import os
import json

_startup_logger = None


def setup_logging(default_path='logging.json', default_level=logging.INFO, env_key='LOG_CFG'):
    """ Setup logging configuration
    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def _init_startup_logger():
    """ Convenience method to initialize the setup error logger.
    """
    if not os.path.exists('/logs/err'):
        # as a fallback to prevent failures, we will just return a plain old logger if the
        # container isn't configured internally for the setup logger.
        return logging.getLogger(__name__)

    formatter = logging.Formatter('[CONTAINER STARTUP ERROR] (%(asctime)s - %(module)s:%(lineno)s): %(message)s')
    handler = logging.FileHandler('/logs/err')
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)

    logger = logging.getLogger('startup_error')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    global _startup_logger
    _startup_logger = logger


def get_startup_logger():
    """ Get the startup logger, used to log out to the Container's stdout.

    Returns:
        Logger: the logger configured to write to the container's stdout,
            assuming other service-specific configurations allow for it.
    """
    if _startup_logger is None:
        _init_startup_logger()
    return _startup_logger
