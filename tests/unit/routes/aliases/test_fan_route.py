"""Test the 'synse.routes.aliases' Synse Server module's fan route.
"""
# pylint: disable=redefined-outer-name,unused-argument,line-too-long

import asynctest
import pytest
from sanic.response import HTTPResponse

import synse.commands
import synse.validate
from synse import errors
from synse.routes.aliases import fan_route
from synse.scheme.base_response import SynseResponse
from tests import utils


def mockwritereturn(rack, board, device, data):
    """Mock method that will be used in monkeypatching the write command."""
    r = SynseResponse()
    r.data = {'data': data}
    return r


@pytest.fixture()
def mock_write(monkeypatch):
    """Fixture to monkeypatch the underlying Synse command."""
    mock = asynctest.CoroutineMock(synse.commands.write, side_effect=mockwritereturn)
    monkeypatch.setattr(synse.commands, 'write', mock)
    return mock_write


def mockreadreturn(rack, board, device):
    """Mock method that will be used in monkeypatching the read command."""
    r = SynseResponse()
    r.data = {'value': 1}
    return r


@pytest.fixture()
def mock_read(monkeypatch):
    """Fixture to monkeypatch the underlying Synse command."""
    mock = asynctest.CoroutineMock(synse.commands.read, side_effect=mockreadreturn)
    monkeypatch.setattr(synse.commands, 'read', mock)
    return mock_read


def mockvalidatedevicetype(device_type, rack, board, device):
    """Mock method that will be used in mokeypatching the validate device type method."""
    return


@pytest.fixture()
def mock_validate_device_type(monkeypatch):
    """Fixture to monkeypatch the validate_device_type method."""
    mock = asynctest.CoroutineMock(synse.validate.validate_device_type, side_effect=mockvalidatedevicetype)
    monkeypatch.setattr(synse.validate, 'validate_device_type', mock)
    return mock_validate_device_type


@pytest.mark.asyncio
async def test_synse_fan_read(mock_validate_device_type, mock_read, no_pretty_json):
    """Test a successful read."""

    r = utils.make_request('/synse/fan')

    result = await fan_route(r, 'rack-1', 'vec', '123456')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"value":1}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_fan_write_invalid(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing fan speed with an invalid speed specified."""

    r = utils.make_request('/synse/fan?speed=test')

    try:
        await fan_route(r, 'rack-1', 'vec', '123456')
    except errors.SynseError as e:
        assert e.error_id == errors.INVALID_ARGUMENTS
        assert 'test' in e.args[0]


@pytest.mark.asyncio
async def test_synse_fan_write_valid(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing fan speed (rpm) with a valid target specified."""

    r = utils.make_request('/synse/fan?speed=500')

    result = await fan_route(r, 'rack-1', 'vec', '123456')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"data":{"action":"speed","raw":"500"}}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_fan_route_bad_param(mock_validate_device_type, mock_write, no_pretty_json):
    """Test setting fan, passing an unsupported query param."""

    r = utils.make_request('/synse/fan?unsupported=true')

    with pytest.raises(errors.InvalidArgumentsError):
        await fan_route(r, 'rack-1', 'vec', '123456')


@pytest.mark.asyncio
async def test_synse_fan_route_by_percent(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing fan speed (percent) with a valid target specified."""

    r = utils.make_request('/synse/fan?speed_percent=50')

    result = await fan_route(r, 'rack-1', 'vec', '123456')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"data":{"action":"speed_percent","raw":"50"}}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_fan_route_bad_params(mock_validate_device_type, mock_write, no_pretty_json):
    """Test setting fan, passing both 'speed' and 'speed_percent' params,
    which is not supported."""

    r = utils.make_request('/synse/fan?speed=100&speed_percent=50')

    with pytest.raises(errors.InvalidArgumentsError):
        await fan_route(r, 'rack-1', 'vec', '123456')
