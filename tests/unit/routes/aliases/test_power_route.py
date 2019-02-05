"""Test the 'synse_server.routes.aliases' Synse Server module's power route."""

import asynctest
import pytest
from sanic.response import HTTPResponse

import synse_server.commands
import synse_server.validate
from synse_server import errors
from synse_server.routes.aliases import power_route
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
    mock = asynctest.CoroutineMock(
        synse_server.validate.validate_device_type,
        side_effect=mockvalidatedevicetype
    )
    monkeypatch.setattr(synse_server.validate, 'validate_device_type', mock)
    return mock_validate_device_type


@pytest.mark.asyncio
async def test_synse_power_read(mock_validate_device_type, mock_read, no_pretty_json):
    """Test a successful read."""

    r = utils.make_request('/synse/power')

    result = await power_route(r, 'rack-1', 'vec', '123456')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"value":1}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_power_write_invalid(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing power state with an invalid state specified."""

    r = utils.make_request('/synse/power?state=test')

    with pytest.raises(errors.InvalidUsage):
        await power_route(r, 'rack-1', 'vec', '123456')


@pytest.mark.asyncio
async def test_synse_power_write_valid_1(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing power state with a valid state specified."""

    r = utils.make_request('/synse/power?state=on')

    result = await power_route(r, 'rack-1', 'vec', '123456')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"data":{"action":"state","raw":"on"}}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_power_write_valid_2(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing power state with a valid state specified."""

    r = utils.make_request('/synse/power?state=off')

    result = await power_route(r, 'rack-1', 'vec', '123456')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"data":{"action":"state","raw":"off"}}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_power_write_valid_3(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing power state with a valid state specified."""

    r = utils.make_request('/synse/power?state=cycle')

    result = await power_route(r, 'rack-1', 'vec', '123456')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"data":{"action":"state","raw":"cycle"}}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_power_route_bad_param(mock_validate_device_type, mock_write, no_pretty_json):
    """Test setting power, passing an unsupported query param."""

    r = utils.make_request('/synse/power?unsupported=true')

    with pytest.raises(errors.InvalidUsage):
        await power_route(r, 'rack-1', 'vec', '123456')
