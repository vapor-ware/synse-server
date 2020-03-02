"""Synse Server application logging."""

import logging
import logging.config
import sys

import structlog
from sanic import app, asgi, handlers, request, server
from structlog import contextvars

from synse_server import config

logging_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        'root': {
            'level': 'INFO',
            'handlers': ['default'],
        },
        'synse_server': {
            'level': 'INFO',
            'handlers': ['default'],
            'propagate': True,
        },
        'sanic.root': {
            'level': 'INFO',
            'handlers': ['default'],
        },
        'sanic.error': {
            'level': 'INFO',
            'handlers': ['error'],
            'propagate': True,
            'qualname': 'sanic.error',
        },
    },
    'handlers': {
        'default': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        },
        'error': {
            'class': 'logging.StreamHandler',
            'stream': sys.stderr,
        },
    },
}

logging.config.dictConfig(logging_config)

structlog.configure(
    processors=[
        contextvars.merge_contextvars,
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.KeyValueRenderer(
            key_order=['timestamp', 'logger', 'level', 'event']
        ),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


def override_sanic_loggers():
    # Override Sanic loggers with structlog loggers. Unfortunately
    # there isn't a great way of doing this because the Sanic modules
    # already hold a reference to the logging.Logger at import load,
    # so we are stuck with just replacing those references in their
    # respective modules.
    root = structlog.get_logger('sanic.root')
    error = structlog.get_logger('sanic.error')

    app.error_logger = error
    app.logger = root
    asgi.logger = root
    handlers.logger = root
    request.logger = root
    request.error_logger = error
    server.logger = root


override_sanic_loggers()


def setup_logger() -> None:
    """Configure the Synse Server logger."""
    level = logging.getLevelName(config.options.get('logging', 'info').upper())
    structlog.get_logger('synse_server').setLevel(level)
