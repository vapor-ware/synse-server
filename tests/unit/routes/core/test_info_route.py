"""Test the 'synse.routes.core' Synse Server module's info route."""
# pylint: disable=redefined-outer-name,unused-argument

import asynctest
import pytest
from sanic.response import HTTPResponse

import synse.commands
from synse.routes.core import info_route
from synse.scheme.base_response import SynseResponse


def mockreturn(rack, board, device):
    """Mock method that will be used in monkeypatching the command."""
    r = SynseResponse()
    r.data = {'r': rack, 'b': board, 'd': device}
    return r


@pytest.fixture()
def mock_info(monkeypatch):
    """Fixture to monkeypatch the underlying Synse command."""
    mock = asynctest.CoroutineMock(synse.commands.info, side_effect=mockreturn)
    monkeypatch.setattr(synse.commands, 'info', mock)
    return mock_info


@pytest.mark.asyncio
async def test_synse_info_route(mock_info, no_pretty_json):
    """Test successfully getting the info."""

    result = await info_route(None, 'rack1', 'board1', 'device1')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"r":"rack1","b":"board1","d":"device1"}'
    assert result.status == 200


@pytest.mark.asyncio
async def test_synse_info_route_no_optional(mock_info, no_pretty_json):
    """Test successfully getting the info without optional params specified."""

    result = await info_route(None, 'rack1')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"r":"rack1","b":null,"d":null}'
    assert result.status == 200
