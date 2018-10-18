"""Test the 'synse.routes.core' Synse Server module's read cached route."""
# pylint: disable=unused-argument

import asynctest
import pytest
from sanic.response import StreamingHTTPResponse

import synse.commands
from synse.routes.core import read_cached_route
from synse.scheme.base_response import SynseResponse
from tests import utils


@pytest.mark.asyncio
async def test_synse_read_cached_route(monkeypatch):
    """Test a successful read cache request."""

    # monkeypatch the read_cached command
    def _mock(*args, **kwargs):
        r = SynseResponse()
        r.data = {'value': 1}  # data doesn't matter here
        return r
    mocked = asynctest.CoroutineMock(synse.commands.read_cached, side_effect=_mock)
    monkeypatch.setattr(synse.commands, 'read_cached', mocked)

    result = await read_cached_route(
        utils.make_request('/synse/readcached'),
    )

    assert isinstance(result, StreamingHTTPResponse)
    assert result.status == 200
