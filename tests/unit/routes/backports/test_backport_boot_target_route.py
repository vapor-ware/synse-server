"""Test the 'synse.routes.backports' Synse Server module's boot target route.
"""
# pylint: disable=redefined-outer-name,unused-argument

import asynctest
import pytest
from sanic.response import HTTPResponse
from tests import utils

import synse.routes.aliases
from synse import config, errors
from synse.routes.backports import backport_boot_target_route
from synse.scheme.base_response import SynseResponse


def mockwritereturn(rack, board, device, data):
    """Mock method that will be used in monkeypatching the write command."""
    r = SynseResponse()
    r.data = {'data': data}
    return r


@pytest.fixture()
def mock_write(monkeypatch):
    """Fixture to monkeypatch the underlying Synse command."""
    mock = asynctest.CoroutineMock(synse.routes.aliases.commands.write, side_effect=mockwritereturn)
    monkeypatch.setattr(synse.routes.aliases.commands, 'write', mock)
    return mock_write


def mockreadreturn(rack, board, device):
    """Mock method that will be used in monkeypatching the read command."""
    r = SynseResponse()
    r.data = {'value': 1}
    return r


@pytest.fixture()
def no_pretty_json():
    """Fixture to ensure basic JSON responses."""
    config.options['pretty_json'] = False


@pytest.mark.asyncio
async def test_synse_backport_boot_target_write_invalid(mock_write, no_pretty_json):
    """Test writing boot target with an invalid target specified."""

    r = utils.make_request('/synse/boot_target/test')

    try:
        await backport_boot_target_route(r, 'rack-1', 'vec', '123456', 'test')
    except errors.SynseError as e:
        assert e.error_id == errors.INVALID_ARGUMENTS
        assert 'test' in e.args[0]


@pytest.mark.asyncio
async def test_synse_backport_boot_target_write_valid_1(mock_write, no_pretty_json):
    """Test writing boot target with a valid target specified."""

    r = utils.make_request('/synse/boot_target/pxe')

    result = await backport_boot_target_route(r, 'rack-1', 'vec', '123456', 'pxe')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"data":{"action":"target","raw":"pxe"}}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_backport_boot_target_write_valid_2(mock_write, no_pretty_json):
    """Test writing boot target with a valid target specified."""

    r = utils.make_request('/synse/boot_target/hdd')

    result = await backport_boot_target_route(r, 'rack-1', 'vec', '123456', 'hdd')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"data":{"action":"target","raw":"hdd"}}'
    assert result.status == 200
