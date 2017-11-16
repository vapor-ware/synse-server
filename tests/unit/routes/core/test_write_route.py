"""Test the 'synse.routes.core' Synse Server module's write route."""
# pylint: disable=redefined-outer-name,unused-argument

import asynctest
import pytest
from sanic.exceptions import InvalidUsage
from sanic.response import HTTPResponse
from tests import utils

import synse.commands
from synse import config
from synse.errors import SynseError
from synse.routes.core import write_route
from synse.scheme.base_response import SynseResponse


def mockreturn(rack, board, device, data):
    """Mock method that will be used in monkeypatching the command."""
    r = SynseResponse()
    r.data = {'r': rack, 'b': board, 'd': device}
    return r


@pytest.fixture()
def mock_write(monkeypatch):
    """Fixture to monkeypatch the underlying Synse command."""
    mock = asynctest.CoroutineMock(synse.commands.write, side_effect=mockreturn)
    monkeypatch.setattr(synse.commands, 'write', mock)
    return mock_write


@pytest.fixture()
def no_pretty_json():
    """Fixture to ensure basic JSON responses."""
    config.options['pretty_json'] = False


@pytest.mark.asyncio
async def test_synse_write_route(mock_write, no_pretty_json):
    """Test a successful write."""

    data = {
        'action': 'color',
        'raw': [b'00ff55']
    }

    r = utils.make_request('/synse/write', data)

    result = await write_route(r, 'rack-1', 'vec', '123456')
    expected = '{"r":"rack-1","b":"vec","d":"123456"}'

    assert isinstance(result, HTTPResponse)
    assert result.body == expected.encode('ascii')
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_write_route_bad_json(mock_write, no_pretty_json):
    """Write when invalid JSON is posted."""

    data = '{{/.'

    r = utils.make_request('/synse/write')
    r.body = data

    with pytest.raises(InvalidUsage):
        await write_route(r, 'rack-1', 'vec', '123456')


@pytest.mark.asyncio
async def test_synse_write_route_invalid_json(mock_write, no_pretty_json):
    """Write when 'raw' and 'action' are not in the given request body."""

    data = {
        'key1': 'color',
        'key2': [b'00ff55']
    }

    r = utils.make_request('/synse/write', data)

    with pytest.raises(SynseError):
        await write_route(r, 'rack-1', 'vec', '123456')


@pytest.mark.asyncio
async def test_synse_write_route_partial_json_ok_1(mock_write, no_pretty_json):
    """Write when the 'action' key is present but the 'raw' field is missing."""

    data = {
        'action': 'color',
        'key2': [b'00ff55']
    }

    r = utils.make_request('/synse/write', data)

    result = await write_route(r, 'rack-1', 'vec', '123456')
    expected = '{"r":"rack-1","b":"vec","d":"123456"}'

    assert isinstance(result, HTTPResponse)
    assert result.body == expected.encode('ascii')
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_write_route_partial_json_ok_2(mock_write, no_pretty_json):
    """Write when the 'raw' key is present but the 'action' field is missing."""

    data = {
        'key1': 'color',
        'raw': [b'00ff55']
    }

    r = utils.make_request('/synse/write', data)

    result = await write_route(r, 'rack-1', 'vec', '123456')
    expected = '{"r":"rack-1","b":"vec","d":"123456"}'

    assert isinstance(result, HTTPResponse)
    assert result.body == expected.encode('ascii')
    assert result.status == 200
