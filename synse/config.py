"""Synse Server configurations and configuration helpers.
"""

from bison import Bison, DictOption, Option, Scheme

# The Synse Server configuration scheme
scheme = Scheme(
    Option('logging', default='info', choices=['debug', 'info', 'warning', 'error', 'critical']),
    Option('pretty_json', default=True, field_type=bool),
    Option('locale', default='en_US', field_type=str),
    DictOption('plugin', default={}, scheme=Scheme(
        DictOption('tcp', default={}, scheme=None, bind_env=True),
        DictOption('unix', default={}, scheme=None, bind_env=True)
    )),
    DictOption('cache', default=None, scheme=Scheme(
        DictOption('meta', scheme=Scheme(
            Option('ttl', default=20, field_type=int)
        )),
        DictOption('transaction', scheme=Scheme(
            Option('ttl', default=300, field_type=int)  # five minutes
        ))
    )),
    DictOption('grpc', scheme=Scheme(
        Option('timeout', default=3, field_type=int)
    )),
)

# Configuration options manager for Synse Server. All access to configuration
# data should be done through `options`.
options = Bison(scheme)
