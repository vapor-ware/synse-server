"""

"""

import sys

import configargparse

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'standard': {
            'format': '%(asctime)s - (%(name)s)[%(levelname)s] %(module)s:%(lineno)s: %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
    },
    'handlers': {
        'debug': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'DEBUG',
            'stream': sys.stderr
        },
        'error': {
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
            'level': 'ERROR',
            'stream': sys.stderr
        }
    },
    'loggers': {
        'synse': {
            'level': 'DEBUG',
            'handlers': ['debug', 'error']
        }
    },
    'root': {
        'propagate': False,
        'handlers': ['error']
    }
}


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


options = {}


def load(opts=None):
    """

    Args:
        opts (dict): a dictionary containing the configuration to read.
    """
    global options
    options = vars(parser.parse_args(opts))
