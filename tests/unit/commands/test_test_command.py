"""Test the 'synse.commands.test' Synse Server module."""

import pytest

from synse.commands import test
from synse.scheme.test import TestResponse


@pytest.mark.asyncio
async def test_test_command():
    """Get a test response."""

    t = await test()
    assert isinstance(t, TestResponse)
