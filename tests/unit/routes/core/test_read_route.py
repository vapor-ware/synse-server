"""Test the 'synse.routes.core' Synse Server module's read route.
"""

import asynctest
import pytest

from sanic.response import HTTPResponse

import synse.commands
from synse import config
from synse.scheme.base_response import SynseResponse
from synse.routes.core import read_route


def mockreturn(rack, board, device):
    r = SynseResponse()
    r.data = {'value': 1}
    return r


@pytest.fixture()
def mock_read(monkeypatch):
    mock = asynctest.CoroutineMock(synse.commands.read, side_effect=mockreturn)
    monkeypatch.setattr(synse.commands, 'read', mock)
    return mock_read


@pytest.fixture()
def no_pretty_json():
    config.options['pretty_json'] = False


@pytest.mark.asyncio
async def test_synse_read_route(mock_read, no_pretty_json):
    """
    """
    result = await read_route(None, 'rack-1', 'vec', '123456')

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"value":1}'
    assert result.status == 200
