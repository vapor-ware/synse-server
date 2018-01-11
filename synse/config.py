"""Synse Server configurations and configuration helpers.
"""
# pylint: disable=line-too-long

import sys

import configargparse

LOGGING = dict(
    version=1,
    disable_existing_loggers=False,

    formatters={
        'standard': {
            'format': '%(asctime)s - (%(name)s)[%(levelname)s] %(module)s:%(lineno)s: %(message)s',
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
            'handlers': ['access'],
            'propagate': True,
            'qualname': 'sanic.access'
        },
        'synse': {
            'level': 'INFO',
            'handlers': ['access']
        }
    }
)


AIOCACHE = {
    'default': {
        'cache': 'aiocache.SimpleMemoryCache',
        'serializer': {
            'class': 'aiocache.serializers.NullSerializer'
        }
    }
}


parser = configargparse.ArgParser(
    default_config_files=[
        '/synse/config/config.yml'
    ]
)


parser.add('--config-file', is_config_file=True, help='config file path')
parser.add('--debug', env_var='DEBUG', type=bool, default=False, help='run synse in debug mode')

parser.add('--pretty_json', type=bool, default=False, help='make the json returned by endpoints pretty')

server_group = parser.add_argument_group('server', 'options for configuring the webserver')

server_group.add('--port', env_var='SERVER_PORT', default=5000, type=int, help='port to listen on')
server_group.add('--host', env_var='SERVER_HOST', default='0.0.0.0', type=str, help='the host to run the server on')

parser.add('--locale', env_var='SYNSE_LANG', default='en_US', type=str, choices=['en_US'], help='Locale code for Synse logs and errors.')

options = {}


def load(opts=None):
    """Load the Synse Server configuration from the parser.

    Args:
        opts (dict): a dictionary containing the configuration to read.
    """
    global options
    options = vars(parser.parse_args(opts))
