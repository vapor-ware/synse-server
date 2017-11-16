"""Test the 'synse.commands.info' Synse Server module.
"""

import asynctest
import pytest

from synse import errors
import synse.cache
from synse.commands.info import info, get_resources
from synse.scheme.info import InfoResponse


def mockreturn():
    """Mock method that will be used in monkeypatching the command."""
    return {
        'rack-1': {
            'rack': 'rack-1',
            'boards': {
                'vec': {
                    'board': 'vec',
                    'devices': {
                        '12345': {
                            'device': '12345',
                            'type': 'thermistor'
                        }
                    }
                }
            }
        }
    }


@pytest.fixture()
def mock_info(monkeypatch):
    """Fixture to monkeypatch the underlying Synse cache lookup."""
    mock = asynctest.CoroutineMock(synse.cache.get_resource_info_cache, side_effect=mockreturn)
    monkeypatch.setattr(synse.cache, 'get_resource_info_cache', mock)
    return mock_info


@pytest.mark.asyncio
async def test_info_command_rack(mock_info):
    """Get an InfoResponse when only a rack is specified."""

    resp = await info('rack-1')

    assert isinstance(resp, InfoResponse)
    assert resp.data == {
        'rack': 'rack-1',
        'boards': [
            'vec'
        ]
    }


@pytest.mark.asyncio
async def test_info_command_rack_board(mock_info):
    """Get an InfoResponse when a rack and board are specified."""

    resp = await info('rack-1', 'vec')

    assert isinstance(resp, InfoResponse)
    assert resp.data == {
        'board': 'vec',
        'location': {
            'rack': 'rack-1'
        },
        'devices': [
            '12345'
        ]
    }


@pytest.mark.asyncio
async def test_info_command_rack_board_device(mock_info):
    """Get an InfoResponse when a rack, board, and device are specified."""

    resp = await info('rack-1', 'vec', '12345')

    assert isinstance(resp, InfoResponse)
    assert resp.data == {
        'device': '12345',
        'type': 'thermistor'
    }


@pytest.mark.asyncio
async def test_info_command_no_rack(mock_info):
    """Get an InfoResponse when a rack is not specified."""

    with pytest.raises(errors.SynseError):
        await info(None)


@pytest.mark.asyncio
async def test_info_command_invalid_rack(mock_info):
    """Get an InfoResponse when an invalid rack is specified."""

    with pytest.raises(errors.SynseError):
        await info(rack='foo')


@pytest.mark.asyncio
async def test_info_command_invalid_board(mock_info):
    """Get an InfoResponse when an invalid board is specified."""

    with pytest.raises(errors.SynseError):
        await info(rack='rack-1', board='foo')


@pytest.mark.asyncio
async def test_info_command_invalid_device(mock_info):
    """Get an InfoResponse when an invalid device is specified."""

    with pytest.raises(errors.SynseError):
        await info(rack='rack-1', board='vec', device='foo')


def test_get_resources_all_none():
    """Get resources when rack, board, device are None."""

    cache = mockreturn()
    r, b, d = get_resources(cache)

    assert r is None
    assert b is None
    assert d is None


def test_get_resources_rack():
    """Get resources when only rack is specified."""

    cache = mockreturn()
    r, b, d = get_resources(cache, 'rack-1')

    assert r == cache['rack-1']
    assert b is None
    assert d is None


def test_get_resources_rack_board():
    """Get resources when a board and rack are specified."""

    cache = mockreturn()
    r, b, d = get_resources(cache, 'rack-1', 'vec')

    assert r == cache['rack-1']
    assert b == cache['rack-1']['boards']['vec']
    assert d is None


def test_get_resources_rack_board_device():
    """Get resources when a rack, board, and device are specified."""

    cache = mockreturn()
    r, b, d = get_resources(cache, 'rack-1', 'vec', '12345')

    assert r == cache['rack-1']
    assert b == cache['rack-1']['boards']['vec']
    assert d == cache['rack-1']['boards']['vec']['devices']['12345']


def test_get_resources_nonexistent_rack():
    """Get resources for a non-existent rack."""

    cache = mockreturn()
    with pytest.raises(errors.SynseError):
        get_resources(cache, rack='foo')


def test_get_resources_nonexistent_board():
    """Get resources for a non-existent board."""

    cache = mockreturn()
    with pytest.raises(errors.SynseError):
        get_resources(cache, rack='rack-1', board='bar')


def test_get_resources_nonexistent_device():
    """Get resources for a non-existent device."""

    cache = mockreturn()
    with pytest.raises(errors.SynseError):
        get_resources(cache, rack='rack-1', board='vec', device='abcdef')
