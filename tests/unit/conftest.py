"""Test configuration for Synse Server unit tests."""

import os

import bison
import pytest

from synse import cache, config, const, plugin
from tests import data_dir


@pytest.fixture(autouse=True)
def reset_state():
    """Fixture to reset all Synse Server state between tests."""

    _old = const.SOCKET_DIR
    const.SOCKET_DIR = data_dir

    yield

    # reset configuration
    config.options = bison.Bison(config.scheme)
    config.options.env_prefix = 'SYNSE'
    config.options.auto_env = True

    # reset managed plugins
    plugin.Plugin.manager.plugins = {}

    # clear the environment
    for k, _ in os.environ.items():
        if k.startswith('SYNSE_'):
            del os.environ[k]

    # reset the socket directory
    const.SOCKET_DIR = _old


@pytest.fixture()
async def clear_caches():
    """Fixture to clear all caches before a test starts."""
    await cache.clear_all_meta_caches()
    await cache.clear_cache(cache.NS_TRANSACTION)
