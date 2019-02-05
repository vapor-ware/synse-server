"""Test the 'synse_server.scheme.config' Synse Server module."""

from synse_server import config
from synse_server.scheme.config import ConfigResponse


def test_config_scheme():
    """Test that the config scheme matches the expected."""
    config.options._override = {'debug': False, 'pretty_json': True, 'some_key': 1}

    response_scheme = ConfigResponse()

    # the config response just gives back the synse server config
    assert len(response_scheme.data) == 3
    assert response_scheme.data == {
        'debug': False,
        'pretty_json': True,
        'some_key': 1
    }


def test_config_scheme_hidden_value():
    """Test that the config scheme matches the expected when a value is marked as hidden."""
    config.options._override = {'debug': False, 'pretty_json': True, '_some_key': 1}

    response_scheme = ConfigResponse()

    # the config response just gives back the synse server config
    assert len(response_scheme.data) == 2
    assert response_scheme.data == {
        'debug': False,
        'pretty_json': True
    }
