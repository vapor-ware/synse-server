"""Test the 'synse.response' Synse Server module.
"""

from sanic.response import HTTPResponse

from synse import response
from synse import config


def test_json():
    """
    """
    data = {'test': 'value'}
    actual = response.json(data)

    assert isinstance(actual, HTTPResponse)
    assert actual.body == b'{"test":"value"}'


def test_json_pretty():
    """
    """
    config.options['pretty_json'] = True

    data = {'test': 'value'}
    actual = response.json(data)

    assert isinstance(actual, HTTPResponse)
    assert actual.body == b'{\n  "test":"value"\n}'
