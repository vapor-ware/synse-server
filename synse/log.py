"""Synse Server application logging.
"""

import logging

from synse import config

logger = logging.getLogger('synse')


def setup_logger(level=logging.INFO):
    """Configure the Synse Server logger.

    Args:
        level (int): The logging level to set the 'synse' logger to.
    """
    if config.options.get('debug'):
        level = logging.DEBUG
    logger.setLevel(level)
