"""Test the 'synse.scheme.config' Synse Server module.
"""
# pylint: disable=redefined-outer-name,unused-argument

import pytest

from synse import config
from synse.scheme.config import ConfigResponse


@pytest.fixture()
def set_config():
    """Fixture to set the global Synse Server config to some test values."""
    config.options = {'debug': False, 'pretty_json': True, 'some_key': 1}


@pytest.fixture()
def set_config_hidden():
    """Fixture to set the global Synse Server config to some test values, with one hidden."""
    config.options = {'debug': False, 'pretty_json': True, '_some_key': 1}


def test_config_scheme(set_config):
    """Test that the config scheme matches the expected.
    """
    response_scheme = ConfigResponse()

    # the config response just gives back the synse server config
    assert len(response_scheme.data) == 3
    assert response_scheme.data == {
        'debug': False,
        'pretty_json': True,
        'some_key': 1
    }


def test_config_scheme_hidden_value(set_config_hidden):
    """Test that the config scheme matches the expected when a value is marked as hidden.
    """
    response_scheme = ConfigResponse()

    # the config response just gives back the synse server config
    assert len(response_scheme.data) == 2
    assert response_scheme.data == {
        'debug': False,
        'pretty_json': True
    }
