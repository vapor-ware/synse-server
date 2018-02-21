"""Synse Server application logging.
"""

import logging

from synse import config

logger = logging.getLogger('synse')

levels = dict(
    debug=logging.DEBUG,
    info=logging.INFO,
    warning=logging.WARNING,
    error=logging.ERROR,
    critical=logging.CRITICAL
)


def setup_logger(level=logging.INFO):
    """Configure the Synse Server logger.

    Args:
        level (int): The default logging level to set the 'synse' logger to
            if no configuration is available.
    """
    level = levels.get(config.options.get('logging'), level)
    logger.setLevel(level)
