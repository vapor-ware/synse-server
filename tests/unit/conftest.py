"""Test configuration for Synse Server unit tests.
"""

import os
import shutil

import pytest

from synse import cache, config, const, plugin
from synse.proto import client
from tests import data_dir


@pytest.fixture(scope='module', autouse=True)
def tmp_dir():
    """Fixture to create and remove the _tmp dir, used to hold test data."""
    if not os.path.isdir(data_dir):
        os.mkdir(data_dir)

    yield
    if os.path.isdir(data_dir):
        shutil.rmtree(data_dir)


@pytest.fixture(autouse=True)
def clear_tmp_dir():
    """Clear the _tmp directory of test data between tests."""
    yield
    for f in os.listdir(data_dir):
        path = os.path.join(data_dir, f)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.unlink(path)


@pytest.fixture(autouse=True)
def reset_state():
    """Fixture to reset all Synse Server state between tests."""

    _old = const.SOCKET_DIR
    const.SOCKET_DIR = data_dir

    yield

    # reset configuration
    config.options = {}

    # reset managed plugins
    plugin.Plugin.manager.plugins = {}

    # clear out the state of the client manager
    client.SynseInternalClient._client_stubs = {}

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
