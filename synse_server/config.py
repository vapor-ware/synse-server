"""Synse Server configuration and scheme definition."""

from bison import Bison, DictOption, ListOption, Option, Scheme

# The Synse Server configuration scheme
scheme = Scheme(
    Option('logging', default='debug', choices=['debug', 'info', 'warning', 'error', 'critical']),
    Option('pretty_json', default=True, field_type=bool),
    DictOption('plugin', default={}, scheme=Scheme(
        ListOption('tcp', default=[], member_type=str, bind_env=True),
        ListOption('unix', default=[], member_type=str, bind_env=True),
        DictOption('discover', required=False, bind_env=True, scheme=Scheme(
            DictOption('kubernetes', required=False, bind_env=True, scheme=Scheme(
                Option('namespace', required=False, bind_env=True, field_type=str),
                DictOption('endpoints', required=False, bind_env=True, scheme=Scheme(
                    DictOption('labels', bind_env=True, scheme=None)
                )),
            ))
        )),
    )),
    DictOption('cache', default=None, scheme=Scheme(
        DictOption('device', scheme=Scheme(
            Option('rebuild_every', default=180, field_type=int),  # three minutes
        )),
        DictOption('plugin', scheme=Scheme(
            Option('refresh_every', default=120, field_type=int),  # two minutes
        )),
        DictOption('transaction', scheme=Scheme(
            Option('ttl', default=300, field_type=int),  # five minutes
        ))
    )),
    DictOption('grpc', scheme=Scheme(
        Option('timeout', default=3, field_type=int),
        DictOption('tls', required=False, bind_env=True, scheme=Scheme(
            Option('cert', field_type=str)
        ))
    )),
    DictOption('ssl', required=False, scheme=Scheme(
        Option('cert', bind_env=True, field_type=str),
        Option('key', bind_env=True, field_type=str),
    )),
    DictOption('metrics', scheme=Scheme(
        Option('enabled', default=False, bind_env=True, field_type=bool),
    )),
)

# Configuration options manager for Synse Server. All access to configuration
# data should be done through `options`.
options = Bison(scheme)
