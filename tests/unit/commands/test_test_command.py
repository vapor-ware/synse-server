"""Test the 'synse.commands.test' Synse Server module."""

import pytest

from synse import commands
from synse.scheme.test import TestResponse as TR


@pytest.mark.asyncio
async def test_test_command():
    """Get a test response."""

    t = await commands.test()
    assert isinstance(t, TR)
