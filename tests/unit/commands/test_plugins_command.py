"""Test the 'synse.commands.plugins' Synse Server module."""

import pytest

from synse.commands.plugins import get_plugins
from synse.scheme.plugins import PluginsResponse


@pytest.mark.asyncio
async def test_plugins_command():
    """Get a plugins response."""

    c = await get_plugins()
    assert isinstance(c, PluginsResponse)
