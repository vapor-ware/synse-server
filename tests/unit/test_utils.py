"""Test the 'synse.utils' Synse Server module.
"""

from synse import utils


def test_composite():
    """Test successfully composing various string combinations."""
    cases = {
        'r-b-d': ('r', 'b', 'd'),
        '0-1-2': ('0', '1', '2'),
        'abcdefghijk--1234567890': ('abcdefghijk', '', '1234567890')
    }

    for expected, params in cases.items():
        actual = utils.composite(params[0], params[1], params[2])
        assert expected == actual
