"""Test the 'synse.commands.config' Synse Server module."""

import pytest

from synse.commands import config
from synse.scheme.config import ConfigResponse


@pytest.mark.asyncio
async def test_config_command():
    """Get a configuration response."""

    c = await config()
    assert isinstance(c, ConfigResponse)
