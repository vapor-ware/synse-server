"""Test the 'synse.commands.scan' Synse Server module.
"""

import asynctest
import pytest

import synse.cache
import synse.plugin
from synse import errors
from synse.commands.scan import scan
from synse.scheme.scan import ScanResponse


def mockreturn():
    """Mock method that will be used in monkeypatching the command."""
    return {
        'racks': [
            {
                'rack_id': 'rack-1',
                'boards': [
                    {
                        'board_id': 'vec',
                        'devices': [
                            {
                                'device_id': '1e93da83dd383757474f539314446c3d',
                                'device_info': 'Rack Temperature Spare',
                                'device_type': 'temperature'
                            },
                            {
                                'device_id': '18185208cbc0e5a4700badd6e39bb12d',
                                'device_info': 'Rack Temperature Middle Rear',
                                'device_type': 'temperature'
                            }
                        ]
                    }
                ]
            }
        ]
    }


def mockregister():
    """Mock method to ignore side effects of calling `register_plugins`."""
    return True


@pytest.fixture()
def mock_scan(monkeypatch):
    """Fixture to monkeypatch the underlying Synse cache lookup."""
    mock = asynctest.CoroutineMock(synse.cache.get_scan_cache, side_effect=mockreturn)
    monkeypatch.setattr(synse.cache, 'get_scan_cache', mock)
    return mock_scan


@pytest.fixture()
def mock_register(monkeypatch):
    """Fixture to monkeypatch the plugin's register_plugins method."""
    monkeypatch.setattr(synse.plugin, 'register_plugins', mockregister)
    return mock_register


@pytest.mark.asyncio
async def test_scan_command(mock_scan, mock_register):
    """Get a ScanResponse when no filter specified."""

    resp = await scan()

    assert isinstance(resp, ScanResponse)
    assert resp.data == mockreturn()


@pytest.mark.asyncio
async def test_scan_command_rack(mock_scan, mock_register):
    """Get a ScanResponse when a good rack filter specified."""

    resp = await scan(rack='rack-1')

    assert isinstance(resp, ScanResponse)
    assert resp.data == mockreturn()['racks'][0]


@pytest.mark.asyncio
async def test_scan_command_rack_invalid(mock_scan, mock_register):
    """Get a ScanResponse when a bad rack filter specified."""

    with pytest.raises(errors.SynseError):
        await scan(rack='foo')


@pytest.mark.asyncio
async def test_scan_command_board(mock_scan, mock_register):
    """Get a ScanResponse when a good board filter specified."""

    resp = await scan(rack='rack-1', board='vec')

    assert isinstance(resp, ScanResponse)
    assert resp.data == mockreturn()['racks'][0]['boards'][0]


@pytest.mark.asyncio
async def test_scan_command_board_invalid(mock_scan, mock_register):
    """Get a ScanResponse when a bad board filter specified."""

    with pytest.raises(errors.SynseError):
        await scan(rack='rack-1', board='bar')


@pytest.mark.asyncio
async def test_scan_command_forced(mock_scan, mock_register):
    """Get a ScanResponse when it is forced."""

    resp = await scan(force=True)

    assert isinstance(resp, ScanResponse)
    assert resp.data == mockreturn()
