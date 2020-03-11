"""Unit tests for the ``synse_server.cmd.config`` module."""

import pytest

from synse_server import cmd


@pytest.mark.asyncio
async def test_config_no_items(mocker):
    # Mock test data
    mocker.patch.dict('synse_server.config.options._full_config', {})

    # --- Test case -----------------------------
    resp = await cmd.config()
    assert resp == {}


@pytest.mark.asyncio
async def test_config_reserved_items(mocker):
    # Mock test data
    mocker.patch.dict('synse_server.config.options._full_config', {
        '_a': 1,
        '_b': 2,
        '_c': 3,
    })

    # --- Test case -----------------------------
    resp = await cmd.config()
    assert resp == {}


@pytest.mark.asyncio
async def test_config_with_items(mocker):
    # Mock test data
    mocker.patch.dict('synse_server.config.options._full_config', {
        'a': 1,
        'b': 2,
        'c': 3,
    })

    # --- Test case -----------------------------
    resp = await cmd.config()
    assert resp == {
        'a': 1,
        'b': 2,
        'c': 3,
    }


@pytest.mark.asyncio
async def test_config_with_mixed_items(mocker):
    # Mock test data
    mocker.patch.dict('synse_server.config.options._full_config', {
        'a': 1,
        'b': 2,
        'c': 3,
        '_d': 4,
        '_e': 5,
    })

    # --- Test case -----------------------------
    resp = await cmd.config()
    assert resp == {
        'a': 1,
        'b': 2,
        'c': 3,
    }
