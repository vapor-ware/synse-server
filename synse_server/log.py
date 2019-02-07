"""Synse Server application logging."""

import logging
import sys

import structlog

from synse_server import config

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt='iso'),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.KeyValueRenderer(
            key_order=['timestamp', 'level', 'event'],
        ),
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)


logger = structlog.get_logger('synse-server')


# TODO: could do something like this I guess.. see how this could tie in to structlog though.
import logging

l = logging.getLogger('sanic.access')
l.addHandler()

d = logging.getLogger('sanic.error')
d.addHandler()


def setup_logger():
    """Configure the Synse Server logger."""
    level = logging.getLevelName(config.options.get('logging', 'info').upper())

    # TODO: instead of using the mallet that is basicConfig, we should exercise
    #  more care into how the loggers are defined to:
    #    a.) prevent duplicate logs via logger propagation
    #    b.) ensure that logs are all output in a common format.
    #  this might take a little work (and possibly monkeying) with how Sanic
    #  does its logging.
    logging.basicConfig(
        format='%(message)s',
        stream=sys.stdout,
        level=level,
    )
