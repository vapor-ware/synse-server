"""Test the 'synse.utils' Synse Server module."""

import pytest

from synse import utils


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
