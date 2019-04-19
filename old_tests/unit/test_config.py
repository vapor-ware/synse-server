"""Test the 'synse_server.config' Synse Server module."""

from synse_server.config import options


def test_defaults():
    """Check that the config defaults are set properly."""

    # parse and validate so the defaults are loaded
    options.parse(requires_cfg=False)
    options.validate()

    assert options.config == {
        'logging': 'info',
        'pretty_json': True,
        'locale': 'en_US',
        'plugin': {
            'tcp': [],
            'unix': [],
        },
        'cache': {
            'meta': {
                'ttl': 20
            },
            'transaction': {
                'ttl': 300
            }
        },
        'grpc': {
            'timeout': 3
        },
    }
