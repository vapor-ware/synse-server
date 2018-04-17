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


@pytest.mark.parametrize(
    'val,expected', [
        ('true', True),
        ('True', True),
        ('TRUE', True),
        ('tRuE', True),
        ('false', False),
        ('False', False),
        ('FALSE', False),
        ('fAlSe', False),
    ]
)
def test_s_to_bool(val, expected):
    """Test successfully converting from string to bool."""
    actual = utils.s_to_bool(val)
    assert expected == actual


@pytest.mark.parametrize(
    'val', [
        'a',
        '',
        '1',
        '0',
        'yes',
        'no',
    ]
)
def test_s_to_bool_invalid(val):
    """Test unsuccessfully converting from string to bool."""
    with pytest.raises(ValueError):
        utils.s_to_bool(val)


@pytest.mark.parametrize(
    'val,expected', [
        ('0', 0),
        ('2', 2),
        ('256', 256),
        ('9999999', 9999999),
        ('-1', -1),
        ('-2953', -2953),
        ('0.0', 0),
        ('0.1', 0),
        ('12.5', 12),
        ('-5.0', -5),
        ('-12.5', -12),
    ]
)
def test_s_to_int(val, expected):
    """Test successfully converting from string to int"""
    actual = utils.s_to_int(val)
    assert expected == actual


@pytest.mark.parametrize(
    'val', [
        'abc',
        '...',
        'true',
        'false',
        'e^2',
    ]
)
def test_s_to_int_invalid(val):
    """Test unsuccessfully converting from string to int"""
    with pytest.raises(ValueError):
        utils.s_to_int(val)
