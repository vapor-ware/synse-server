"""Test the 'synse.commands.plugins' Synse Server module."""
# pylint: disable=redefined-outer-name,unused-argument

import os
import shutil
import socket

import pytest

from synse import plugin
from synse.commands.plugins import get_plugins
from synse.scheme.plugins import PluginsResponse


@pytest.fixture()
def mock_plugin():
    """Convenience fixture to create a test plugin."""
    # create a temp dir to hold the socket
    if not os.path.isdir('tmp'):
        os.mkdir('tmp')

    # create the socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind('tmp/test-plug')

    p = plugin.Plugin(
        name='test-plug',
        address='tmp/test-plug',
        mode='unix'
    )

    yield p

    sock.shutdown(2)
    sock.close()
    try:
        os.unlink('tmp/test-plug')
    except OSError:
        if os.path.exists('tmp/test-plug'):
            raise


@pytest.fixture()
def disable_register():
    """Disable plugin registration."""
    # plugin registration will remove plugins from the manager that are
    # not found to be 'active' any longer, where 'active' is defined as
    # being present/absent from the expected directory. In some test setups,
    # the plugins won't be in standard places so we disable registration.
    def passthru():
        """Passthrough function for testing."""
        return
    plugin.register_plugins = passthru


@pytest.fixture(scope='module')
def remove_tmp_dir():
    """Fixture to remove any test data."""
    if os.path.isdir('tmp'):
        shutil.rmtree('tmp')


@pytest.fixture()
def cleanup(remove_tmp_dir):
    """Fixture to reset the PluginManager state between tests."""
    yield
    plugin.Plugin.manager.plugins = {}


@pytest.mark.asyncio
async def test_plugins_command_no_plugin():
    """Get a plugins response using no plugin."""
    c = await get_plugins()
    assert isinstance(c, PluginsResponse)
    assert len(c.data) == 0


@pytest.mark.asyncio
async def test_plugins_command_plugin(mock_plugin, disable_register, cleanup):
    """Get a plugins response using plugin."""
    # Add a mock plugin to the Manager
    pm = plugin.Plugin.manager

    # the plugin tested here is added via the mock_plugin fixture
    assert len(pm.plugins) == 1
    assert 'test-plug' in pm.plugins

    # Get that plugin
    c = await get_plugins()
    assert isinstance(c, PluginsResponse)
    assert len(c.data) == 1
    assert c.data == [
        {
            'name': 'test-plug',
            'network': 'unix',
            'address': 'tmp/test-plug'
        }
    ]
