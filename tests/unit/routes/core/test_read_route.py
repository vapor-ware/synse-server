"""Test the 'synse.routes.core' Synse Server module's read route."""
# pylint: disable=redefined-outer-name,unused-argument

import asynctest
import pytest
from sanic.response import HTTPResponse

import synse.commands
from synse.routes.core import read_route
from synse.scheme.base_response import SynseResponse
from tests import utils


def mockreturn(rack, board, device):
    """Mock method that will be used in monkeypatching the command."""
    r = SynseResponse()
    r.data = {'value': 1}
    return r


@pytest.fixture()
def mock_read(monkeypatch):
    """Fixture to monkeypatch the underlying Synse command."""
    mock = asynctest.CoroutineMock(synse.commands.read, side_effect=mockreturn)
    monkeypatch.setattr(synse.commands, 'read', mock)
    return mock_read


@pytest.mark.asyncio
async def test_synse_read_route(mock_read, no_pretty_json):
    """Test a successful read."""

    result = await read_route(
        utils.make_request('/synse/read'),
        'rack-1', 'vec', '123456'
    )

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"value":1}'
    assert result.status == 200
