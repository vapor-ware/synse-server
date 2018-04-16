"""Test the 'synse.routes.base' Synse Server module's test route."""
# pylint: disable=redefined-outer-name,unused-argument

import pytest
import ujson
from sanic.response import HTTPResponse

from synse.routes.base import test_route as synse_test_route
from tests import utils


@pytest.mark.asyncio
async def test_synse_test_route():
    """Test successfully hitting the test route."""

    result = await synse_test_route(utils.make_request('/synse/test'))

    assert isinstance(result, HTTPResponse)
    assert result.status == 200

    body = ujson.loads(result.body)
    assert 'status' in body
    assert 'timestamp' in body
    assert body['status'] == 'ok'
