"""Synse Server application logging."""

import logging
import sys

from synse_server import config

logger = logging.getLogger('synse')

LOGGING = dict(
    version=1,
    disable_existing_loggers=False,

    formatters={
        'standard': {
            'format': '%(asctime)s - (%(name)s)[%(levelname)s] %(module)s:%(lineno)s: %(message)s',
            'datefmt': '[%Y-%m-%d %H:%M:%S %z]',
            'class': 'logging.Formatter'
        },
        'sanic_access': {
            'format': '%(asctime)s - (%(name)s)[%(levelname)s] %(module)s:%(lineno)s: ' +
                      '"%(request)s %(message)s %(status)d %(byte)d"',
            'datefmt': '[%Y-%m-%d %H:%M:%S %z]',
            'class': 'logging.Formatter'
        }
    },
    handlers={
        'access': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': sys.stdout
        },
        'sanic_access': {
            'class': 'logging.StreamHandler',
            'formatter': 'sanic_access',
            'stream': sys.stdout
        },
        'error': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': sys.stderr
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'stream': sys.stdout
        }
    },
    loggers={
        'root': {
            'level': 'INFO',
            'handlers': ['console']
        },
        'sanic.error': {
            'level': 'INFO',
            'handlers': ['error'],
            'propagate': True,
            'qualname': 'sanic.error'
        },
        'sanic.access': {
            'level': 'INFO',
            'handlers': ['sanic_access'],
            'propagate': True,
            'qualname': 'sanic.access'
        },
        'synse': {
            'level': 'INFO',
            'handlers': ['access']
        }
    }
)

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
            if no level is available via the configuration.
    """
    level = levels.get(config.options.get('logging'), level)
    logger.setLevel(level)
