"""Test the 'synse.response' Synse Server module."""

from sanic.response import HTTPResponse

from synse import config, response


def test_json():
    """Test parsing dict to JSON string."""
    data = {'test': 'value'}
    actual = response.json(data)

    assert isinstance(actual, HTTPResponse)
    assert actual.body == b'{"test":"value"}'


def test_json_pretty():
    """Test parsing dict to a pretty JSON string."""
    config.options['pretty_json'] = True

    data = {'test': 'value'}
    actual = response.json(data)

    assert isinstance(actual, HTTPResponse)
    assert actual.body == b'{\n  "test":"value"\n}'
