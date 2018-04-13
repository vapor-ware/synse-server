"""Test the 'synse.routes.core' Synse Server module's config route."""
# pylint: disable=redefined-outer-name,unused-argument

import asynctest
import pytest
from sanic.response import HTTPResponse

import synse.commands
from synse.routes.core import config_route
from synse.scheme.base_response import SynseResponse
from tests import utils


def mockreturn():
    """Mock method that will be used in monkeypatching the command."""
    r = SynseResponse()
    r.data = {'test': 'config'}
    return r


@pytest.fixture()
def mock_config(monkeypatch):
    """Fixture to monkeypatch the underlying Synse command."""
    mock = asynctest.CoroutineMock(synse.commands.config, side_effect=mockreturn)
    monkeypatch.setattr(synse.commands, 'config', mock)
    return mock_config


@pytest.mark.asyncio
async def test_synse_config_route(mock_config, no_pretty_json):
    """Test successfully getting the config."""

    result = await config_route(utils.make_request('/synse/config'))

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"test":"config"}'
    assert result.status == 200
