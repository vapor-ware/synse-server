"""Unit tests for the ``synse_server.cmd.version`` module."""

import pytest

import synse_server
from synse_server import cmd


@pytest.mark.asyncio
async def test_version():

    response = await cmd.version()

    assert response == {
        'version': synse_server.__version__,
        'api_version': synse_server.__api_version__,
    }
