"""Test the 'synse.routes.core' Synse Server module's scan route.
"""

import asynctest
import pytest

from sanic.response import HTTPResponse
from sanic.request import Request

import synse.commands
from synse import config
from synse.scheme.base_response import SynseResponse
from synse.routes.core import scan_route


def mockreturn(rack, board, force):
    r = SynseResponse()
    r.data = {'r': rack, 'b': board, 'forced': force}
    return r


@pytest.fixture()
def mock_scan(monkeypatch):
    mock = asynctest.CoroutineMock(synse.commands.scan, side_effect=mockreturn)
    monkeypatch.setattr(synse.commands, 'scan', mock)
    return mock_scan


@pytest.fixture()
def no_pretty_json():
    config.options['pretty_json'] = False


@pytest.mark.asyncio
async def test_synse_scan_route(mock_scan, no_pretty_json):
    """
    """
    r = Request(
        url_bytes=b'/synse/scan',
        headers={},
        version=None,
        method=None,
        transport=None
    )

    result = await scan_route(r)

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"r":null,"b":null,"forced":false}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_scan_route_with_rack(mock_scan, no_pretty_json):
    """
    """
    r = Request(
        url_bytes=b'/synse/scan',
        headers={},
        version=None,
        method=None,
        transport=None
    )

    result = await scan_route(r, 'rack-1')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"r":"rack-1","b":null,"forced":false}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_scan_route_with_rack_and_board(mock_scan, no_pretty_json):
    """
    """
    r = Request(
        url_bytes=b'/synse/scan',
        headers={},
        version=None,
        method=None,
        transport=None
    )

    result = await scan_route(r, 'rack-1', 'vec')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"r":"rack-1","b":"vec","forced":false}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_scan_route_forced(mock_scan, no_pretty_json):
    """
    """
    r = Request(
        url_bytes=b'/synse/scan?force=true',
        headers={},
        version=None,
        method=None,
        transport=None
    )

    result = await scan_route(r)

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"r":null,"b":null,"forced":true}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_scan_route_forced_2(mock_scan, no_pretty_json):
    """
    """
    r = Request(
        url_bytes=b'/synse/scan?force=yes',
        headers={},
        version=None,
        method=None,
        transport=None
    )

    result = await scan_route(r)

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"r":null,"b":null,"forced":false}'
    assert result.status == 200
