"""Test the 'synse_server.routes.aliases' Synse Server module's led route."""

import asynctest
import pytest
import ujson
from sanic.response import HTTPResponse
from synse_grpc import api

import synse_server.commands
import synse_server.validate
from synse_server import errors
from synse_server.routes.aliases import led_route
from synse_server.scheme.base_response import SynseResponse
from synse_server.scheme.write import WriteResponse
from tests import utils


def mockwritereturn(rack, board, device, data):
    """Mock method that will be used in monkeypatching the write command."""
    r = WriteResponse({
        '{}-{}-{}'.format(rack, board, device): api.WriteData(
            action=data.get('action'),
            data=data.get('raw').encode('ascii')
        )
    })
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
async def test_synse_led_read(mock_validate_device_type, mock_read, no_pretty_json):
    """Test a successful read."""

    r = utils.make_request('/synse/led')

    result = await led_route(r, 'rack-1', 'vec', '123456')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"value":1}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_led_write_invalid_1(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing LED state with an invalid state specified."""

    r = utils.make_request('/synse/led?state=test')

    with pytest.raises(errors.InvalidUsage):
        await led_route(r, 'rack-1', 'vec', '123456')


@pytest.mark.asyncio
async def test_synse_led_write_invalid_2(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing LED state with an invalid state specified."""

    r = utils.make_request('/synse/led?state=foo')

    with pytest.raises(errors.InvalidUsage):
        await led_route(r, 'rack-1', 'vec', '123456')


@pytest.mark.asyncio
async def test_synse_led_write_invalid_3(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing LED state with an invalid state specified."""

    r = utils.make_request('/synse/led?color=xyz')

    with pytest.raises(errors.InvalidUsage):
        await led_route(r, 'rack-1', 'vec', '123456')


@pytest.mark.asyncio
async def test_synse_led_write_invalid_4(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing LED state with an invalid state specified."""

    r = utils.make_request('/synse/led?state=on&color=bar')

    with pytest.raises(errors.InvalidUsage):
        await led_route(r, 'rack-1', 'vec', '123456')


@pytest.mark.asyncio
async def test_synse_led_write_invalid_5(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing LED state with an invalid state specified."""

    r = utils.make_request('/synse/led?color=1000000')

    with pytest.raises(errors.InvalidUsage):
        await led_route(r, 'rack-1', 'vec', '123456')


@pytest.mark.asyncio
async def test_synse_led_write_invalid_6(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing LED state with an invalid state specified."""

    r = utils.make_request('/synse/led?color=-FF')

    with pytest.raises(errors.InvalidUsage):
        await led_route(r, 'rack-1', 'vec', '123456')


@pytest.mark.asyncio
async def test_synse_led_write_valid_1(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing LED state with a valid state specified."""

    r = utils.make_request('/synse/led?state=on')

    result = await led_route(r, 'rack-1', 'vec', '123456')

    assert isinstance(result, HTTPResponse)
    assert result.body == \
        b'[{"context":{"action":"state","data":"on"},"transaction":"rack-1-vec-123456"}]'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_led_write_valid_2(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing LED state with a valid state specified."""

    r = utils.make_request('/synse/led?state=off')

    result = await led_route(r, 'rack-1', 'vec', '123456')

    assert isinstance(result, HTTPResponse)
    assert result.body == \
        b'[{"context":{"action":"state","data":"off"},"transaction":"rack-1-vec-123456"}]'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_led_write_valid_3(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing LED state with a valid state specified."""

    r = utils.make_request('/synse/led?state=blink')

    result = await led_route(r, 'rack-1', 'vec', '123456')

    assert isinstance(result, HTTPResponse)
    assert result.body == \
        b'[{"context":{"action":"state","data":"blink"},"transaction":"rack-1-vec-123456"}]'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_led_write_valid_5(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing LED state with a valid state specified."""

    r = utils.make_request('/synse/led?color=ffffff')

    result = await led_route(r, 'rack-1', 'vec', '123456')

    assert isinstance(result, HTTPResponse)
    assert result.body == \
        b'[{"context":{"action":"color","data":"ffffff"},"transaction":"rack-1-vec-123456"}]'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_led_write_valid_6(mock_validate_device_type, mock_write, no_pretty_json):
    """Test writing LED state with a valid state specified."""

    r = utils.make_request('/synse/led?color=ffffff&state=on')

    result = await led_route(r, 'rack-1', 'vec', '123456')

    expected = [
        {'context': {'action': 'state', 'data': b'on'}, 'transaction': 'rack-1-vec-123456'},
        {'context': {'action': 'color', 'data': b'ffffff'}, 'transaction': 'rack-1-vec-123456'}
    ]

    expected_json = ujson.dumps(expected)

    assert isinstance(result, HTTPResponse)
    assert result.body == expected_json.encode('ascii')
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_led_route_bad_param(mock_validate_device_type, mock_write, no_pretty_json):
    """Test setting led, passing an unsupported query param."""

    r = utils.make_request('/synse/led?unsupported=true')

    with pytest.raises(errors.InvalidUsage):
        await led_route(r, 'rack-1', 'vec', '123456')
