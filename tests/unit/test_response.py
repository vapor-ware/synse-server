"""Test the 'synse.response' Synse Server module."""

import pytest
from sanic.response import HTTPResponse

from synse import config, response


@pytest.mark.parametrize(
    'data,expected', [
        ({'test': 'value'}, b'{"test":"value"}'),
        ({'test': 1}, b'{"test":1}'),
        ({'test': 1.3}, b'{"test":1.3}'),
        ({'test': None}, b'{"test":null}'),
        ({'test': False}, b'{"test":false}'),
    ]
)
def test_json(data, expected):
    """Test parsing dict to JSON string."""
    actual = response.json(data)

    assert isinstance(actual, HTTPResponse)
    assert expected == actual.body


@pytest.mark.parametrize(
    'data,expected', [
        ({'test': 'value'}, b'{\n  "test":"value"\n}\n'),
        ({'test': 1}, b'{\n  "test":1\n}\n'),
        ({'test': 1.3}, b'{\n  "test":1.3\n}\n'),
        ({'test': None}, b'{\n  "test":null\n}\n'),
        ({'test': False}, b'{\n  "test":false\n}\n'),
    ]
)
def test_json_pretty(data, expected):
    """Test parsing dict to a pretty JSON string."""
    config.options.set('pretty_json', True)

    actual = response.json(data)

    assert isinstance(actual, HTTPResponse)
    assert expected == actual.body
