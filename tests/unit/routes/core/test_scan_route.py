"""Test the 'synse_server.routes.core' Synse Server module's scan route."""
# pylint: disable=redefined-outer-name,unused-argument

import asynctest
import pytest
from sanic.response import HTTPResponse

import synse_server.commands
from synse_server import errors
from synse_server.routes.core import scan_route
from synse_server.scheme.base_response import SynseResponse
from tests import utils


def mockreturn(rack, board, force):
    """Mock method that will be used in monkeypatching the command."""
    r = SynseResponse()
    r.data = {'r': rack, 'b': board, 'forced': force}
    return r


@pytest.fixture()
def mock_scan(monkeypatch):
    """Fixture to monkeypatch the underlying Synse command."""
    mock = asynctest.CoroutineMock(synse_server.commands.scan, side_effect=mockreturn)
    monkeypatch.setattr(synse_server.commands, 'scan', mock)
    return mock_scan


@pytest.mark.asyncio
async def test_synse_scan_route(mock_scan, no_pretty_json):
    """Test a successful scan."""

    r = utils.make_request('/synse/scan')

    result = await scan_route(r)

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"r":null,"b":null,"forced":false}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_scan_route_with_rack(mock_scan, no_pretty_json):
    """Test performing a scan with a rack specified."""

    r = utils.make_request('/synse/scan')

    result = await scan_route(r, 'rack-1')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"r":"rack-1","b":null,"forced":false}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_scan_route_with_rack_and_board(mock_scan, no_pretty_json):
    """Test performing a scan with a rack and board specified."""

    r = utils.make_request('/synse/scan')

    result = await scan_route(r, 'rack-1', 'vec')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"r":"rack-1","b":"vec","forced":false}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_scan_route_forced(mock_scan, no_pretty_json):
    """Test forcing a rescan successfully."""

    r = utils.make_request('/synse/scan?force=true')

    result = await scan_route(r)

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"r":null,"b":null,"forced":true}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_scan_route_forced_2(mock_scan, no_pretty_json):
    """Test forcing a rescan, but using an unrecognized value."""

    r = utils.make_request('/synse/scan?force=yes')

    result = await scan_route(r)

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"r":null,"b":null,"forced":false}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_scan_route_bad_param(mock_scan, no_pretty_json):
    """Test scanning, passing an unsupported query param."""

    r = utils.make_request('/synse/scan?unsupported=true')

    with pytest.raises(errors.InvalidArgumentsError):
        await scan_route(r)
