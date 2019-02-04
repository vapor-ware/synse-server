"""Synse Server application logging."""
# pylint: disable=line-too-long

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


# TODO (etd): keeping this commented out for now to use as a future reference. We
#  still need to get Sanic logs working through structlog ()
# LOGGING = dict(
#     version=1,
#     disable_existing_loggers=False,
#
#     formatters={
#         'standard': {
#             'format': '%(asctime)s - (%(name)s)[%(levelname)s] %(module)s:%(lineno)s: %(message)s',
#             'datefmt': '[%Y-%m-%d %H:%M:%S %z]',
#             'class': 'logging.Formatter'
#         },
#         'sanic_access': {
#             'format': '%(asctime)s - (%(name)s)[%(levelname)s] %(module)s:%(lineno)s: ' +
#                       '"%(request)s %(message)s %(status)d %(byte)d"',
#             'datefmt': '[%Y-%m-%d %H:%M:%S %z]',
#             'class': 'logging.Formatter'
#         }
#     },
#     handlers={
#         'access': {
#             'class': 'logging.StreamHandler',
#             'formatter': 'standard',
#             'stream': sys.stdout
#         },
#         'sanic_access': {
#             'class': 'logging.StreamHandler',
#             'formatter': 'sanic_access',
#             'stream': sys.stdout
#         },
#         'error': {
#             'class': 'logging.StreamHandler',
#             'formatter': 'standard',
#             'stream': sys.stderr
#         },
#         'console': {
#             'class': 'logging.StreamHandler',
#             'formatter': 'standard',
#             'stream': sys.stdout
#         }
#     },
#     loggers={
#         'root': {
#             'level': 'INFO',
#             'handlers': ['console']
#         },
#         'sanic.error': {
#             'level': 'INFO',
#             'handlers': ['error'],
#             'propagate': True,
#             'qualname': 'sanic.error'
#         },
#         'sanic.access': {
#             'level': 'INFO',
#             'handlers': ['sanic_access'],
#             'propagate': True,
#             'qualname': 'sanic.access'
#         },
#         'synse': {
#             'level': 'INFO',
#             'handlers': ['access']
#         }
#     }
# )

def setup_logger():
    """Configure the Synse Server logger."""
    level = logging.getLevelName(config.options.get('logging', 'info').upper())
    logging.basicConfig(
        format='%(message)s',
        stream=sys.stdout,
        level=level,
    )
