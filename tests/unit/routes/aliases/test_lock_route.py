"""Test the 'synse_server.routes.aliases' Synse Server module's lock route."""
# pylint: disable=redefined-outer-name,unused-argument,line-too-long

import asynctest
import pytest
from sanic.response import HTTPResponse

import synse_server.commands
import synse_server.validate
from synse_server import errors
from synse_server.routes.aliases import lock_route
from synse_server.scheme.base_response import SynseResponse
from tests import utils


def mockwritereturn(rack, board, device, data):
    """Mock method that will be used in monkeypatching the write command."""
    r = SynseResponse()
    r.data = {'data': data}
    return r


@pytest.fixture()
def mock_write(monkeypatch):
    """Fixture to monkeypatch the underlying Synse command."""
    mock = asynctest.CoroutineMock(synse_server.commands.write, side_effect=mockwritereturn)
    monkeypatch.setattr(synse_server.commands, 'write', mock)
    return mock_write


def mockreadreturn(rack, board, device):
    """Mock method that will be used in monkeypatching the read command."""
    r = SynseResponse()
    r.data = {'value': 1}
    return r


@pytest.fixture()
def mock_read(monkeypatch):
    """Fixture to monkeypatch the underlying Synse command."""
    mock = asynctest.CoroutineMock(synse_server.commands.read, side_effect=mockreadreturn)
    monkeypatch.setattr(synse_server.commands, 'read', mock)
    return mock_read


def mockvalidatedevicetype(device_type, rack, board, device):
    """Mock method that will be used in mokeypatching the validate device type method."""


@pytest.fixture()
def mock_validate_device_type(monkeypatch):
    """Fixture to monkeypatch the validate_device_type method."""
    mock = asynctest.CoroutineMock(synse_server.validate.validate_device_type, side_effect=mockvalidatedevicetype)
    monkeypatch.setattr(synse_server.validate, 'validate_device_type', mock)
    return mock_validate_device_type


@pytest.mark.asyncio
async def test_synse_lock_read(mock_validate_device_type, mock_read, no_pretty_json):
    """Test a successful read."""

    r = utils.make_request('/synse/lock')

    result = await lock_route(r, 'rack-1', 'vec', '123456')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"value":1}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_lock_write_invalid(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing lock state with an invalid state specified."""

    r = utils.make_request('/synse/lock?action=test')

    try:
        await lock_route(r, 'rack-1', 'vec', '123456')
    except errors.SynseError as e:
        assert e.error_id == errors.INVALID_ARGUMENTS
        assert 'test' in e.args[0]


@pytest.mark.asyncio
async def test_synse_lock_write_valid_1(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing lock state with a valid state specified."""

    r = utils.make_request('/synse/lock?action=unlock')

    result = await lock_route(r, 'rack-1', 'vec', '123456')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"data":{"action":"unlock"}}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_lock_write_valid_2(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing lock state with a valid state specified."""

    r = utils.make_request('/synse/lock?action=lock')

    result = await lock_route(r, 'rack-1', 'vec', '123456')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"data":{"action":"lock"}}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_lock_write_valid_3(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing lock state with a valid state specified."""

    r = utils.make_request('/synse/lock?action=pulseUnlock')

    result = await lock_route(r, 'rack-1', 'vec', '123456')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"data":{"action":"pulseUnlock"}}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_lock_route_bad_param(mock_validate_device_type, mock_write, no_pretty_json):
    """Test setting lock, passing an unsupported query param."""

    r = utils.make_request('/synse/lock?unsupported=true')

    with pytest.raises(errors.InvalidArgumentsError):
        await lock_route(r, 'rack-1', 'vec', '123456')
