"""Test the 'synse.routes.backports' Synse Server module's fan route.
"""
# pylint: disable=redefined-outer-name,unused-argument

import asynctest
import pytest
from sanic.response import HTTPResponse
from tests import utils

import synse.commands
from synse import config, errors
from synse.routes.backports import backport_fan_route
from synse.scheme.base_response import SynseResponse


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


@pytest.fixture()
def no_pretty_json():
    """Fixture to ensure basic JSON responses."""
    config.options['pretty_json'] = False


@pytest.mark.asyncio
@pytest.mark.skip  # TODO - need to implement validation before we can test.
async def test_synse_backport_fan_write_invalid(mock_write, no_pretty_json):
    """Test writing fan speed with an invalid speed specified."""

    r = utils.make_request('/synse/fan/test')

    try:
        await backport_fan_route(r, 'rack-1', 'vec', '123456', 'test')
    except errors.SynseError as e:
        assert e.error_id == errors.INVALID_ARGUMENTS
        assert 'test' in e.args[0]


@pytest.mark.asyncio
async def test_synse_backport_fan_write_valid(mock_write, no_pretty_json):
    """Test writing fan speed with a valid target specified."""

    r = utils.make_request('/synse/fan/500')

    result = await backport_fan_route(r, 'rack-1', 'vec', '123456', '500')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"data":{"action":"speed","raw":"500"}}'
    assert result.status == 200
