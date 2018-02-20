"""Synse Server configurations and configuration helpers.
"""
# pylint: disable=line-too-long

import collections
import logging
import os
import sys

import yaml

logger = logging.getLogger('synse')

CONFIG_ENV_PREFIX = 'SYNSE'
CONFIG_DELIMITER = '.'
DEFAULT_CONFIG_PATH = '/synse/config/config.yml'

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

AIOCACHE = {
    'default': {
        'cache': 'aiocache.SimpleMemoryCache',
        'serializer': {
            'class': 'aiocache.serializers.NullSerializer'
        }
    }
}

# Configs options will be parsed here once the application starts.
options = {}


def load():
    """Parse configurations in the following order:
        - defaults
        - configs files
        - environment variables
    """
    load_default_configs()
    parse_user_configs()
    parse_env_vars()


def load_default_configs():
    """Set the default configurations for the application.
    These configurations will be used in the event that no user configurations are specified.
    """
    global options

    # Specify our default options
    defaults = {
        'locale': 'en_US',
        'pretty_json': False,
        'logging': 'info',
        'cache': {
            'meta': {
                'ttl': 20
            },
            'transaction': {
                'ttl': 20
            }
        },
        'grpc': {
            'timeout': 20
        }
    }

    # Update global config options
    options.update(defaults)


def parse_user_configs():
    """Set the user configurations for the application. These configurations
    will overwrite default configurations.
    """
    global options

    # If a custom configuration file is set through environment variable, use it.
    # Otherwise, use the defaults
    custom_path = os.getenv('SYNSE_CONFIG')
    if custom_path:
        user_configs = load_config_file(custom_path)
    else:
        user_configs = load_config_file(DEFAULT_CONFIG_PATH)

    # Given the result as a dictionary, merge it with our current configs
    merge_dicts(options, user_configs)


def parse_env_vars():
    """Parse the environment variables for the application. These configurations
    have the top precedence order and will overwrite user and defaults.
    """
    # Look for environment variables that start with CONFIG_ENV_PREFIX
    for k, v in os.environ.items():
        if k.startswith(CONFIG_ENV_PREFIX):

            # Contruct the configuration key from the environment variable key
            key = k[len(CONFIG_ENV_PREFIX) + 1:].replace('_', '.').lower()

            # If current key equals to 'config', the value is an user-specified config file path.
            # Just skip it because we already handle it in parsing user configurations stage.
            if key == 'config':
                break

            # Otherwise, validate the value by checking it type and update the pair
            if v.lower() == 'true':
                v = True
            elif v.lower() == 'false':
                v = False
            # For other types, must check the key name manually
            else:
                v = set_value_type(key.split(CONFIG_DELIMITER)[0], v)

            # Update the pair
            update_options(key, v)


def load_config_file(filepath):
    """Load the specified YAML configuration into a dictionary. If no config
    file is specified, the default file is used.

    Args:
        filepath (str): The configuration file path.

    Returns:
        dict: The values loaded from the specified YAML file.
    """
    # List of supported YAML extensions
    yaml_exts = ['.yml', '.yaml']

    if os.path.splitext(filepath)[1] in yaml_exts:
        try:
            with open(filepath, 'r') as config_file:
                return yaml.load(config_file)
        except FileNotFoundError as e:
            logger.error(e)
            raise

    # If not found, raise an error to notify that extension is not supported
    raise ValueError('The file extension is not supported.')


def merge_dicts(dct, merge_dict):
    """Recursively merge dictionaries.

    Instead of updating only top-level keys, it recurses down into
    dicts nested to an arbitrary depth, updating keys.

    Args:
        dct (dict): The dictionary being merged into.
        merge_dict (dict): The dictionary being merged into dct.

    Reference:
        https://gist.github.com/angstwad/bf22d1822c38a92ec0a9#file-dict_merge-py
    """
    try:
        for k, _ in merge_dict.items():
            if k in dct and isinstance(dct[k], dict) and isinstance(merge_dict[k], collections.Mapping):
                merge_dicts(dct[k], merge_dict[k])
            else:
                dct[k] = merge_dict[k]
    except (AttributeError, TypeError) as e:
        logger.error(e)
        raise


def set_value_type(key, value):
    """Set the right value for parsing an environment variable into configs.
    Since the type of an environment variable's value is always a string,
    manually check its type and return the corresponding value based on the key name.

    Args:
        key (str): The key name.
        value (str): The value to be modified.

    Returns:
        str: The value with the right type.
    """
    if key in ('grpc', 'cache'):
        return int(value)

    return str(value)


def update_options(key, value):
    """Set a value for a given key, supporting nested keys. This method assumes that
    all levels of nesting in the config are dictionaries and not lists.

    For example:
        Given the options above, setting a value for tcp requires:
            options['plugin']['tcp']['example'] = 'localhost:5000'

        Using nested key 'plugin.tcp.example', we can just do
            set('plugin.tcp.example', 'localhost:5000')

    Args:
        key (str): The nested key with CONFIG_DELIMITER.
        value: The value to be changed to.
    """
    global options
    scope = options

    # Get a list of keys
    keys_list = key.split(CONFIG_DELIMITER)

    for k in keys_list:

        # If current key is the last one, assign to the value
        if k == keys_list[-1]:
            scope[k] = value
            break

        # If key is not within the current scope,
        # create an empty dictionary for it
        if k not in scope:
            scope[k] = {}

        # Go inside the scope
        scope = scope[k]
