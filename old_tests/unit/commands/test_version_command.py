"""Test the 'synse_server.commands.version' Synse Server module."""

import pytest

from synse_server.commands import version
from synse_server.scheme.version import VersionResponse


@pytest.mark.asyncio
async def test_version_command():
    """Get a version response."""

    v = await version()
    assert isinstance(v, VersionResponse)
