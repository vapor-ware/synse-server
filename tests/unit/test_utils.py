"""Test the 'synse.utils' Synse Server module."""

import pytest

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


def test_s_to_bool():
    """Test successfully converting from string to bool."""
    cases = {
        'true': True,
        'True': True,
        'TRUE': True,
        'tRuE': True,
        'false': False,
        'False': False,
        'FALSE': False,
        'fAlSe': False
    }

    for case, expected in cases.items():
        actual = utils.s_to_bool(case)
        assert actual == expected


def test_s_to_bool_invalid():
    """Test unsuccessfully converting from string to bool."""
    cases = [
        'a',
        '',
        '1',
        '0',
        'yes',
        'no'
    ]

    for case in cases:
        with pytest.raises(ValueError):
            utils.s_to_bool(case)


def test_s_to_int():
    """Test successfully converting from string to int"""
    cases = {
        '0': 0,
        '2': 2,
        '256': 256,
        '9999999': 9999999,
        '-1': -1,
        '-2953': -2953,
        '0.0': 0,
        '0.1': 0,
        '12.5': 12,
        '-5.0': -5,
        '-12.5': -12
    }

    for case, expected in cases.items():
        actual = utils.s_to_int(case)
        assert actual == expected


def test_s_to_int_invalid():
    """Test unsuccessfully converting from string to int"""
    cases = [
        'abc',
        '...',
        'true',
        'false',
        'e^2'
    ]

    for case in cases:
        with pytest.raises(ValueError):
            utils.s_to_int(case)
