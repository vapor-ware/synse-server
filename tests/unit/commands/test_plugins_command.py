"""Test the 'synse_server.commands.plugins' Synse Server module."""
# pylint: disable=redefined-outer-name,unused-argument

import os
import shutil

import pytest
from synse_grpc import api

from synse_server import config, plugin
from synse_server.commands.plugins import get_plugins
from synse_server.proto import client
from synse_server.scheme.plugins import PluginsResponse


@pytest.fixture()
def mock_plugin():
    """Convenience fixture to create a test plugin. We create a TCP
    based plugin for ease of testing.
    """
    p = plugin.Plugin(
        metadata=api.Metadata(
            name='test-plug',
            tag='vaporio/test-plug'
        ),
        address='localhost:9999',
        plugin_client=client.PluginTCPClient(address='localhost:9999')
    )

    yield p


@pytest.fixture()
def disable_register():
    """Disable plugin registration."""

    # plugin registration will remove plugins from the manager that are
    # not found to be 'active' any longer, where 'active' is defined as
    # being present/absent from the expected directory. In some test setups,
    # the plugins won't be in standard places so we disable registration.
    def passthru():
        """Passthrough function for testing."""

    plugin.register_plugins = passthru


# FIXME - should just use the builtin pytest `tmpdir` fixture
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
    config.options.set('grpc.timeout', 0.25)

    # Add a mock plugin to the Manager
    pm = plugin.Plugin.manager

    # the plugin tested here is added via the mock_plugin fixture. the plugin
    # added by the test fixture has the tag vaporio/test-plug, and uses tcp
    # with address localhost:9999 -- with that, we know what the ID should be.
    assert len(pm.plugins) == 1
    assert 'vaporio/test-plug+tcp@localhost:9999' in pm.plugins

    # Get that plugin
    c = await get_plugins()
    assert isinstance(c, PluginsResponse)
    assert len(c.data) == 1
    p = c.data[0]

    assert p['tag'] == 'vaporio/test-plug'
    assert p['name'] == 'test-plug'
    assert p['description'] == ''
    assert p['maintainer'] == ''
    assert p['vcs'] == ''
    assert p['version'] == {
        'plugin_version': '',
        'sdk_version': '',
        'build_date': '',
        'git_commit': '',
        'git_tag': '',
        'arch': '',
        'os': '',
    }
    assert p['network'] == {
        'protocol': 'tcp',
        'address': 'localhost:9999'
    }
    assert p['health']['timestamp'] != ''
    assert p['health']['checks'] == []
    assert p['health']['status'] == 'error'
    assert 'Connect Failed' in p['health']['message']
