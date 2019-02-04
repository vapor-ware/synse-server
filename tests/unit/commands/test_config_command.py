"""Test the 'synse_server.commands.config' Synse Server module."""

import pytest

from synse_server.commands import config
from synse_server.scheme.config import ConfigResponse


@pytest.mark.asyncio
async def test_config_command():
    """Get a configuration response."""

    c = await config()
    assert isinstance(c, ConfigResponse)
