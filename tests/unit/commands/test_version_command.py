"""Test the 'synse.commands.version' Synse Server module."""

import pytest

from synse.commands import version
from synse.scheme.version import VersionResponse


@pytest.mark.asyncio
async def test_version_command():
    """Get a version response."""

    v = await version()
    assert isinstance(v, VersionResponse)
