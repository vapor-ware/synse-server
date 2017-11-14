"""Test the 'synse.routes.core' Synse Server module's config route.
"""

import asynctest
import pytest

from sanic.response import HTTPResponse

import synse.commands
from synse import config
from synse.scheme.base_response import SynseResponse
from synse.routes.core import config_route


def mockreturn():
    r = SynseResponse()
    r.data = {'test': 'config'}
    return r


@pytest.fixture()
def mock_config(monkeypatch):
    mock = asynctest.CoroutineMock(synse.commands.config, side_effect=mockreturn)
    monkeypatch.setattr(synse.commands, 'config', mock)
    return mock_config


@pytest.fixture()
def no_pretty_json():
    config.options['pretty_json'] = False


@pytest.mark.asyncio
async def test_synse_config_route(mock_config, no_pretty_json):
    """
    """
    result = await config_route(None)

    assert isinstance(result, HTTPResponse)
    assert result.body == b'{"test":"config"}'
    assert result.status == 200
