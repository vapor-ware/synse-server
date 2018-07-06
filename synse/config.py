"""Synse Server configuration and scheme definition."""

from bison import Bison, DictOption, ListOption, Option, Scheme

# The Synse Server configuration scheme
scheme = Scheme(
    Option('logging', default='info', choices=['debug', 'info', 'warning', 'error', 'critical']),
    Option('pretty_json', default=True, field_type=bool),
    Option('locale', default='en_US', field_type=str),
    DictOption('plugin', default={}, scheme=Scheme(
        ListOption('tcp', default=[], member_type=str, bind_env=True),
        ListOption('unix', default=[], member_type=str, bind_env=True),
        DictOption('discover', default={}, bind_env=True, scheme=Scheme(
            DictOption('kubernetes', default={}, bind_env=True, scheme=Scheme(
                DictOption('endpoints', default={}, bind_env=True, scheme=Scheme(
                    DictOption('labels', default={}, bind_env=True, scheme=None)
                )),
            ))
        )),
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
