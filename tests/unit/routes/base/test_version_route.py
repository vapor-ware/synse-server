"""Test the 'synse.routes.base' Synse Server module's version route."""
# pylint: disable=redefined-outer-name,unused-argument

import pytest
import ujson
from sanic.response import HTTPResponse

from synse import version
from synse.routes.base import version_route
from tests import utils


@pytest.mark.asyncio
async def test_synse_version_route():
    """Test successfully hitting the version route."""

    result = await version_route(utils.make_request('/synse/version'))

    assert isinstance(result, HTTPResponse)
    assert result.status == 200

    body = ujson.loads(result.body)
    assert 'version' in body
    assert 'api_version' in body

    assert body['version'] == version.__version__
    assert body['api_version'] == version.__api_version__
