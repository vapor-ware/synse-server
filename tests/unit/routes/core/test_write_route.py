"""Test the 'synse.routes.core' Synse Server module's write route.
"""

import asynctest
import pytest
import ujson

from sanic.response import HTTPResponse
from sanic.request import Request
from sanic.exceptions import InvalidUsage

import synse.commands
from synse import config
from synse.errors import SynseError
from synse.scheme.base_response import SynseResponse
from synse.routes.core import write_route


def mockreturn(rack, board, device, data):
    r = SynseResponse()
    r.data = {'r': rack, 'b': board, 'd': device}
    return r


@pytest.fixture()
def mock_write(monkeypatch):
    mock = asynctest.CoroutineMock(synse.commands.write, side_effect=mockreturn)
    monkeypatch.setattr(synse.commands, 'write', mock)
    return mock_write


@pytest.fixture()
def no_pretty_json():
    config.options['pretty_json'] = False


@pytest.mark.asyncio
async def test_synse_write_route(mock_write, no_pretty_json):
    """
    """
    data = {
        'action': 'color',
        'raw': [b'00ff55']
    }

    r = Request(
        url_bytes=b'/synse/write',
        headers={},
        version=None,
        method=None,
        transport=None
    )
    r.body = ujson.dumps(data)

    result = await write_route(r, 'rack-1', 'vec', '123456')
    expected = '{"r":"rack-1","b":"vec","d":"123456"}'

    assert isinstance(result, HTTPResponse)
    assert result.body == expected.encode('ascii')
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_write_route_bad_json(mock_write, no_pretty_json):
    """
    """
    data = '{{/.'

    r = Request(
        url_bytes=b'/synse/write',
        headers={},
        version=None,
        method=None,
        transport=None
    )
    r.body = data

    with pytest.raises(InvalidUsage):
        await write_route(r, 'rack-1', 'vec', '123456')


@pytest.mark.asyncio
async def test_synse_write_route_invalid_json(mock_write, no_pretty_json):
    """
    """
    data = {
        'key1': 'color',
        'key2': [b'00ff55']
    }

    r = Request(
        url_bytes=b'/synse/write',
        headers={},
        version=None,
        method=None,
        transport=None
    )
    r.body = ujson.dumps(data)

    with pytest.raises(SynseError):
        await write_route(r, 'rack-1', 'vec', '123456')


@pytest.mark.asyncio
async def test_synse_write_route_partial_json_ok_1(mock_write, no_pretty_json):
    """
    """
    data = {
        'action': 'color',
        'key2': [b'00ff55']
    }

    r = Request(
        url_bytes=b'/synse/write',
        headers={},
        version=None,
        method=None,
        transport=None
    )
    r.body = ujson.dumps(data)

    result = await write_route(r, 'rack-1', 'vec', '123456')
    expected = '{"r":"rack-1","b":"vec","d":"123456"}'

    assert isinstance(result, HTTPResponse)
    assert result.body == expected.encode('ascii')
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_write_route_partial_json_ok_2(mock_write, no_pretty_json):
    """
    """
    data = {
        'key1': 'color',
        'raw': [b'00ff55']
    }

    r = Request(
        url_bytes=b'/synse/write',
        headers={},
        version=None,
        method=None,
        transport=None
    )
    r.body = ujson.dumps(data)

    result = await write_route(r, 'rack-1', 'vec', '123456')
    expected = '{"r":"rack-1","b":"vec","d":"123456"}'

    assert isinstance(result, HTTPResponse)
    assert result.body == expected.encode('ascii')
    assert result.status == 200
