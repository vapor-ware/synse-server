"""Test the 'synse.errors' Synse Server module."""

from sanic import exceptions

from synse import errors


def test_synse_error():
    """Create a SynseError with no error id specified."""
    e = errors.SynseError('message')

    assert isinstance(e, exceptions.ServerError)
    assert isinstance(e, errors.SynseError)

    assert e.status_code == 500
    assert e.error_id == errors.UNKNOWN
    assert e.args[0] == 'message'


def test_synse_error2():
    """Create a SynseError with an error id specified."""
    e = errors.SynseError('message', errors.DEVICE_NOT_FOUND)

    assert isinstance(e, exceptions.ServerError)
    assert isinstance(e, errors.SynseError)

    assert e.status_code == 500
    assert e.error_id == errors.DEVICE_NOT_FOUND
    assert e.args[0] == 'message'
