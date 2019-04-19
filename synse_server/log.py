"""Synse Server application logging."""

import logging
import logging.config
import sys

import structlog

from synse_server import config

logging.config.dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'root': {
            'level': 'INFO',
            'handlers': ['default']
        },
        'sanic.error': {
            'level': 'INFO',
            'handlers': ['error'],
            'propagate': True,
            'qualname': 'sanic.error'
        },
        'synse-server': {
            'level': 'INFO',
            'handlers': ['default']
        },
    },
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'stream': sys.stdout
        },
        'error': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
            'stream': sys.stderr
        },
    },
    'formatters': {
        'json': {
            'class': 'pythonjsonlogger.jsonlogger.JsonFormatter'
        },
    }
})

# TODO: since we've disabled the sanic access logs in favor of our own logging
#   we may wish to consider returning to using a KeyValueRenderer as that tends
#   is a bit easier to parse visually.
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.stdlib.render_to_log_kwargs,
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger('synse-server')


def setup_logger():
    """Configure the Synse Server logger."""
    level = logging.getLevelName(config.options.get('logging', 'info').upper())
    logger.setLevel(level)
