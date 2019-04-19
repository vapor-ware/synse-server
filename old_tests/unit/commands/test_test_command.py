"""Test the 'synse_server.commands.test' Synse Server module."""

import pytest

from synse_server import commands
from synse_server.scheme.test import TestResponse as TR


@pytest.mark.asyncio
async def test_test_command():
    """Get a test response."""

    t = await commands.test()
    assert isinstance(t, TR)
