"""Test the 'synse_server.utils' Synse Server module."""

import pytest

from synse_server import utils


@pytest.mark.parametrize(
    'params,expected', [
        (('r', 'b', 'd'), 'r-b-d'),
        (('0', '1', '2'), '0-1-2'),
        (('abcdefghijk', '', '1234567890'), 'abcdefghijk--1234567890'),
        (('-', '-', '-'), '-----'),
    ]
)
def test_composite(params, expected):
    """Test successfully composing various string combinations."""
    actual = utils.composite(*params)
    assert expected == actual


@pytest.mark.parametrize(
    'kind,expected', [
        ('foo', 'foo'),
        ('foo.bar', 'bar'),
        ('...temperature', 'temperature'),
        ('device.1.2.3.4.5.6.humidity', 'humidity'),
        ('', '')
    ]
)
def test_type_from_kind(kind, expected):
    """Test getting the device type from the device kind."""
    actual = utils.type_from_kind(kind)
    assert expected == actual
