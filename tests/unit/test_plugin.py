"""Test the 'synse.plugin' Synse Server module."""
# pylint: disable=redefined-outer-name,unused-argument,line-too-long

import os
import socket

import pytest
from synse_grpc import api

import synse.proto.client
from synse import config, errors, plugin
from synse.proto.client import PluginClient, PluginTCPClient, PluginUnixClient
from tests import data_dir


@pytest.fixture()
def mock_client_test_ok(monkeypatch):
    """Fixture to mock a PluginClient's 'test' method with a good response."""
    def patch(self):
        """Patch function for the client 'test' method."""
        return api.Status(ok=True)
    monkeypatch.setattr(synse.proto.client.PluginClient, 'test', patch)
    return mock_client_test_ok


@pytest.fixture()
def mock_client_test_error(monkeypatch):
    """Fixture to mock a PluginClient's 'test' method with a bad response."""
    def patch(self):
        """Patch function for the client 'test' method."""
        return api.Status(ok=False)
    monkeypatch.setattr(PluginClient, 'test', patch)
    return mock_client_test_error


@pytest.fixture()
def mock_client_meta_ok(monkeypatch):
    """Fixture to mock a PluginClient's 'metainfo' method with a good response."""
    def patch(self):
        """Patch function for the client 'metainfo' method."""
        return api.Metadata(
            name='test-plugin',
            tag='vaporio/test-plugin',
            maintainer='vaporio',
            description='test'
        )
    monkeypatch.setattr(PluginClient, 'metainfo', patch)
    return mock_client_meta_ok


@pytest.fixture()
def mock_client_meta_error(monkeypatch):
    """Fixture to mock a PluginClient's 'metainfo' method with a bad response."""
    def patch(self):
        """Patch function for the client 'metainfo' method."""
        raise ValueError('test error')

    monkeypatch.setattr(PluginClient, 'metainfo', patch)
    return mock_client_meta_error


@pytest.fixture()
def mock_plugin():
    """Convenience fixture to create a test plugin. We create a TCP
    based plugin for ease of testing.
    """
    p = plugin.Plugin(
        metadata=api.Metadata(
            name='test-plug'
        ),
        address='localhost:9999',
        plugin_client=PluginTCPClient(address='localhost:9999')
    )
    yield p


@pytest.fixture()
def grpc_timeout():
    """Fixture to set the configured grpc timeout to something low so tests
    do not take a long time when they fail to connect.
    """
    config.options.set('grpc.timeout', 0.25)


def test_plugin_manager_get():
    """Get a value from the Plugin Manager."""
    pm = plugin.PluginManager()
    pm.plugins['test'] = 'foo'
    assert pm.get('test') == 'foo'


def test_plugin_manager_get_no_value():
    """Get a plugin that is not managed by the Manager."""
    pm = plugin.PluginManager()
    assert pm.get('test') is None


def test_plugin_manager_add_invalid():
    """Add an invalid plugin (a string is not a valid plugin)."""
    pm = plugin.PluginManager()
    with pytest.raises(errors.PluginStateError):
        pm.add('plugin')


def test_plugin_manager_add_already_exists(mock_plugin):
    """Add a plugin that is already managed by the Manager."""
    pm = plugin.PluginManager()
    pm.plugins['+tcp@localhost:9999'] = 'foo'
    with pytest.raises(errors.PluginStateError):
        pm.add(mock_plugin)


def test_plugin_manager_add(mock_plugin):
    """Add a plugin to the Manager."""
    pm = plugin.PluginManager()
    assert len(pm.plugins) == 0
    pm.add(mock_plugin)
    assert len(pm.plugins) == 1
    assert '+tcp@localhost:9999' in pm.plugins


def test_plugin_manager_remove(mock_plugin):
    """Remove a plugin from the Manager."""
    pm = plugin.PluginManager()
    pm.plugins['test-plug'] = mock_plugin
    assert len(pm.plugins) == 1
    assert 'test-plug' in pm.plugins

    pm.remove('test-plug')
    assert len(pm.plugins) == 0
    assert 'test-plug' not in pm.plugins


def test_plugin_manager_remove_nonexistent():
    """Remove a plugin from the Manager that is not there."""
    pm = plugin.PluginManager()
    assert len(pm.plugins) == 0
    pm.remove('test')
    assert len(pm.plugins) == 0


def test_plugin_path_not_exist():
    """Create a plugin when the socket doesn't exist."""
    p = plugin.Plugin(
        metadata=api.Metadata(
            name='test'
        ),
        address='some/nonexistent/path',
        plugin_client=PluginUnixClient(address='some/nonexistent/path')
    )
    assert p.protocol == 'unix'
    assert p.name == 'test'


def test_plugin_unix_ok():
    """Create a UNIX plugin successfully"""

    # create a file in the tmp dir for the test
    path = os.path.join(data_dir, 'test')
    # open(path, 'w').close()

    p = plugin.Plugin(
        metadata=api.Metadata(
            name='test'
        ),
        address=path,
        plugin_client=PluginUnixClient(address=path)
    )

    assert p.name == 'test'
    assert p.address == path
    assert p.protocol == 'unix'
    assert p.client is not None
    assert isinstance(p.client, PluginClient)


def test_plugin_tcp_ok():
    """Create a TCP plugin successfully"""

    p = plugin.Plugin(
        metadata=api.Metadata(
            name='test'
        ),
        address='localhost:9999',
        plugin_client=PluginTCPClient(address='localhost:9999')
    )

    assert p.name == 'test'
    assert p.address == 'localhost:9999'
    assert p.protocol == 'tcp'
    assert p.client is not None
    assert isinstance(p.client, PluginClient)


def test_plugins_same_manager(mock_plugin):
    """Check that all plugins have the same manager."""
    assert plugin.Plugin.manager == mock_plugin.manager


def test_get_plugin1():
    """Get a plugin when it doesn't exist."""
    p = plugin.get_plugin('test')
    assert p is None


def test_get_plugin2(mock_plugin):
    """Get a plugin when it does exist."""
    p = plugin.get_plugin('+tcp@localhost:9999')
    assert isinstance(p, plugin.Plugin)
    assert p.name == 'test-plug'
    assert p.address == 'localhost:9999'
    assert p.protocol == 'tcp'


@pytest.mark.asyncio
async def test_get_plugins1():
    """Get all plugins when no plugins exist."""
    with pytest.raises(StopAsyncIteration):
        await plugin.get_plugins().__anext__()


@pytest.mark.asyncio
async def test_get_plugins2(mock_plugin):
    """Get all plugins when some plugins exist."""
    name, p = await plugin.get_plugins().__anext__()
    assert isinstance(p, plugin.Plugin)
    assert name == '+tcp@localhost:9999'
    assert p.name == 'test-plug'
    assert p.address == 'localhost:9999'
    assert p.protocol == 'tcp'


def test_register_plugins_no_default_socks(grpc_timeout):
    """Register plugins when the plugin path doesn't exist."""
    assert len(plugin.Plugin.manager.plugins) == 0
    plugin.register_plugins()
    assert len(plugin.Plugin.manager.plugins) == 0


def test_register_plugins_no_socks(grpc_timeout):
    """Register plugins when no sockets are in the plugin path."""

    # create a non-socket file
    path = os.path.join(data_dir, 'test.txt')
    open(path, 'w').close()

    assert len(plugin.Plugin.manager.plugins) == 0
    plugin.register_plugins()
    assert len(plugin.Plugin.manager.plugins) == 0


def test_register_plugins_ok(grpc_timeout, mock_client_test_ok, mock_client_meta_ok):
    """Register plugins successfully."""
    # create the socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path = '{}/test'.format(data_dir)
    sock.bind(path)

    assert len(plugin.Plugin.manager.plugins) == 0

    # the plugin is not yet in the config
    assert config.options.get('plugin.unix') is None

    plugin.register_plugins()

    # the plugin has been added to the config (because it was
    # in the default socket directory)
    assert path in config.options.get('plugin.unix')

    assert len(plugin.Plugin.manager.plugins) == 1
    assert 'vaporio/test-plugin+unix@' + path in plugin.Plugin.manager.plugins

    p = plugin.Plugin.manager.plugins['vaporio/test-plugin+unix@' + path]
    assert p.name == 'test-plugin'
    assert p.address == path
    assert p.protocol == 'unix'


def test_register_plugins_already_exists(grpc_timeout, mock_client_test_ok, mock_client_meta_ok):
    """Register plugins when the plugins were already registered."""
    # create the socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path = '{}/test'.format(data_dir)
    sock.bind(path)

    assert len(plugin.Plugin.manager.plugins) == 0

    plugin.register_plugins()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert 'vaporio/test-plugin+unix@' + path in plugin.Plugin.manager.plugins

    p = plugin.Plugin.manager.plugins['vaporio/test-plugin+unix@' + path]
    assert p.name == 'test-plugin'
    assert p.address == path
    assert p.protocol == 'unix'

    # now, re-register
    assert len(plugin.Plugin.manager.plugins) == 1

    plugin.register_plugins()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert 'vaporio/test-plugin+unix@' + path in plugin.Plugin.manager.plugins

    p = plugin.Plugin.manager.plugins['vaporio/test-plugin+unix@' + path]
    assert p.name == 'test-plugin'
    assert p.address == path
    assert p.protocol == 'unix'


def test_register_plugins_new(grpc_timeout, mock_client_test_ok, mock_client_meta_ok):
    """Re-register, adding a new plugin."""
    # create the socket
    sock1 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path1 = '{}/foo'.format(data_dir)
    sock1.bind(path1)

    assert len(plugin.Plugin.manager.plugins) == 0

    plugin.register_plugins()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert 'vaporio/test-plugin+unix@' + path1 in plugin.Plugin.manager.plugins

    p = plugin.Plugin.manager.plugins['vaporio/test-plugin+unix@' + path1]
    assert p.name == 'test-plugin'
    assert p.address == path1
    assert p.protocol == 'unix'

    # now, re-register
    sock2 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path2 = '{}/bar'.format(data_dir)
    sock2.bind(path2)

    assert len(plugin.Plugin.manager.plugins) == 1

    plugin.register_plugins()

    assert len(plugin.Plugin.manager.plugins) == 2
    assert 'vaporio/test-plugin+unix@' + path1 in plugin.Plugin.manager.plugins
    assert 'vaporio/test-plugin+unix@' + path2 in plugin.Plugin.manager.plugins

    p = plugin.Plugin.manager.plugins['vaporio/test-plugin+unix@' + path1]
    assert p.name == 'test-plugin'
    assert p.address == path1
    assert p.protocol == 'unix'

    p = plugin.Plugin.manager.plugins['vaporio/test-plugin+unix@' + path2]
    assert p.name == 'test-plugin'
    assert p.address == path2
    assert p.protocol == 'unix'


def test_register_plugins_old(grpc_timeout, mock_client_test_ok, mock_client_meta_ok):
    """Re-register, removing an old plugin."""
    # create the socket
    sock1 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path1 = '{}/foo'.format(data_dir)
    sock1.bind(path1)

    sock2 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path2 = '{}/bar'.format(data_dir)
    sock2.bind(path2)

    assert len(plugin.Plugin.manager.plugins) == 0

    plugin.register_plugins()

    assert len(plugin.Plugin.manager.plugins) == 2
    assert 'vaporio/test-plugin+unix@' + path1 in plugin.Plugin.manager.plugins

    p = plugin.Plugin.manager.plugins['vaporio/test-plugin+unix@' + path1]
    assert p.name == 'test-plugin'
    assert p.address == path1
    assert p.protocol == 'unix'

    p = plugin.Plugin.manager.plugins['vaporio/test-plugin+unix@' + path2]
    assert p.name == 'test-plugin'
    assert p.address == path2
    assert p.protocol == 'unix'

    # remove one of the sockets and re-register.
    try:
        os.unlink(path1)
    except OSError:
        if os.path.exists(path1):
            raise

    assert len(plugin.Plugin.manager.plugins) == 2

    plugin.register_plugins()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert 'vaporio/test-plugin+unix@' + path2 in plugin.Plugin.manager.plugins

    p = plugin.Plugin.manager.plugins['vaporio/test-plugin+unix@' + path2]
    assert p.name == 'test-plugin'
    assert p.address == path2
    assert p.protocol == 'unix'


def test_register_plugins_from_discovery(grpc_timeout, monkeypatch, mock_client_test_ok, mock_client_meta_ok):
    """Register plugins that we get back from discovery."""

    assert len(plugin.Plugin.manager.plugins) == 0

    monkeypatch.setattr(plugin.kubernetes, 'discover', lambda: ['10.0.0.1:5001', '10.0.0.2:5001'])

    plugin.register_plugins()

    assert len(plugin.Plugin.manager.plugins) == 2

    assert 'vaporio/test-plugin+tcp@10.0.0.1:5001' in plugin.Plugin.manager.plugins
    p = plugin.Plugin.manager.plugins['vaporio/test-plugin+tcp@10.0.0.1:5001']
    assert p.name == 'test-plugin'
    assert p.address == '10.0.0.1:5001'
    assert p.protocol == 'tcp'

    assert 'vaporio/test-plugin+tcp@10.0.0.2:5001' in plugin.Plugin.manager.plugins
    p = plugin.Plugin.manager.plugins['vaporio/test-plugin+tcp@10.0.0.2:5001']
    assert p.name == 'test-plugin'
    assert p.address == '10.0.0.2:5001'
    assert p.protocol == 'tcp'


def test_register_unix_plugin_none_defined(grpc_timeout):
    """Test registering unix based plugins when none is specified."""
    assert len(plugin.Plugin.manager.plugins) == 0

    registered = plugin.register_unix()

    assert len(plugin.Plugin.manager.plugins) == 0
    assert isinstance(registered, list)
    assert len(registered) == 0


def test_register_unix_plugin(grpc_timeout, mock_client_test_ok, mock_client_meta_ok):
    """Test registering unix plugin when a configuration is specified"""
    # create the socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path = os.path.join(data_dir, 'foo')
    sock.bind(path)

    assert len(plugin.Plugin.manager.plugins) == 0

    # set a configuration
    config.options.set('plugin.unix', ['tmp'])

    registered = plugin.register_unix()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert isinstance(registered, list)
    assert len(registered) == 1

    assert 'vaporio/test-plugin+unix@' + path in registered

    p = plugin.get_plugin('vaporio/test-plugin+unix@' + path)
    assert p is not None
    assert p.name == 'test-plugin'
    assert p.protocol == 'unix'
    assert p.address == path


def test_register_unix_plugins(grpc_timeout, mock_client_test_ok, mock_client_meta_ok):
    """Test registering unix plugins when multiple configurations are specified"""
    # create sockets
    sock1 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path1 = os.path.join(data_dir, 'foo')
    sock1.bind(path1)

    sock2 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path2 = os.path.join(data_dir, 'bar')
    sock2.bind(path2)

    assert len(plugin.Plugin.manager.plugins) == 0

    # set configurations
    config.options.set('plugin.unix', ['foo', 'bar'])

    registered = plugin.register_unix()

    assert len(plugin.Plugin.manager.plugins) == 2
    assert isinstance(registered, list)
    assert len(registered) == 2

    assert 'vaporio/test-plugin+unix@' + path1 in registered
    assert 'vaporio/test-plugin+unix@' + path2 in registered

    p1 = plugin.get_plugin('vaporio/test-plugin+unix@' + path1)
    assert p1 is not None
    assert p1.name == 'test-plugin'
    assert p1.protocol == 'unix'
    assert p1.address == path1

    p2 = plugin.get_plugin('vaporio/test-plugin+unix@' + path2)
    assert p2 is not None
    assert p2.name == 'test-plugin'
    assert p2.protocol == 'unix'
    assert p2.address == path2


def test_register_unix_plugin_already_exists(grpc_timeout, mock_client_test_ok, mock_client_meta_ok):
    """Test registering unix plugin when the plugin was already registered."""
    # create the socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path = '{}/test'.format(data_dir)
    sock.bind(path)

    assert len(plugin.Plugin.manager.plugins) == 0

    registered = plugin.register_unix()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert isinstance(registered, list)
    assert len(registered) == 1

    assert 'vaporio/test-plugin+unix@' + path in registered

    p = plugin.get_plugin('vaporio/test-plugin+unix@' + path)
    assert p is not None
    assert p.name == 'test-plugin'
    assert p.address == path
    assert p.protocol == 'unix'

    # now, re-register
    assert len(plugin.Plugin.manager.plugins) == 1

    # set the same configuration
    config.options.set('plugin.unix', [data_dir])

    registered = plugin.register_unix()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert isinstance(registered, list)
    assert len(registered) == 1

    assert 'vaporio/test-plugin+unix@' + path in registered

    p = plugin.get_plugin('vaporio/test-plugin+unix@' + path)
    assert p is not None
    assert p.name == 'test-plugin'
    assert p.address == path
    assert p.protocol == 'unix'


def test_register_unix_plugin_no_socket(grpc_timeout):
    """Test registering unix plugin when no socket is bound"""

    assert len(plugin.Plugin.manager.plugins) == 0

    config.options.set('plugin.unix', [data_dir])

    registered = plugin.register_unix()

    assert len(plugin.Plugin.manager.plugins) == 0
    assert isinstance(registered, list)
    assert len(registered) == 0


def test_register_unix_plugin_no_socket_no_path(grpc_timeout):
    """Test registering unix plugin when the path does not exist"""
    assert len(plugin.Plugin.manager.plugins) == 0

    config.options.set('plugin.unix', [os.path.join(data_dir, 'some', 'other', 'path')])

    registered = plugin.register_unix()

    assert len(plugin.Plugin.manager.plugins) == 0
    assert isinstance(registered, list)
    assert len(registered) == 0


def test_register_unix_plugin_no_config_path(grpc_timeout, mock_client_test_ok, mock_client_meta_ok):
    """Test registering unix plugin when a configuration without a path is specified"""
    # create the socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path = '{}/foo'.format(data_dir)
    sock.bind(path)

    assert len(plugin.Plugin.manager.plugins) == 0

    registered = plugin.register_unix()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert isinstance(registered, list)
    assert len(registered) == 1

    assert 'vaporio/test-plugin+unix@' + path in registered

    p = plugin.get_plugin('vaporio/test-plugin+unix@' + path)
    assert p is not None
    assert p.name == 'test-plugin'
    assert p.protocol == 'unix'
    assert p.address == path


def test_register_tcp_plugin_none_defined(grpc_timeout):
    """Test registering TCP based plugins when none is specified."""
    assert len(plugin.Plugin.manager.plugins) == 0

    registered = plugin.register_tcp()

    assert len(plugin.Plugin.manager.plugins) == 0
    assert isinstance(registered, list)
    assert len(registered) == 0


def test_register_tcp_plugin(grpc_timeout, mock_client_test_ok, mock_client_meta_ok):
    """Test registering TCP based plugin when a configuration is specified"""
    assert len(plugin.Plugin.manager.plugins) == 0

    config.options.set('plugin.tcp', ['localhost:5000'])

    registered = plugin.register_tcp()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert isinstance(registered, list)
    assert len(registered) == 1

    assert 'vaporio/test-plugin+tcp@localhost:5000' in registered

    p = plugin.get_plugin('vaporio/test-plugin+tcp@localhost:5000')
    assert p is not None
    assert p.name == 'test-plugin'
    assert p.protocol == 'tcp'
    assert p.address == 'localhost:5000'


def test_register_tcp_plugins(grpc_timeout, mock_client_test_ok, mock_client_meta_ok):
    """Test registering TCP based plugins when multiple configurations are specified"""
    assert len(plugin.Plugin.manager.plugins) == 0

    config.options.set('plugin.tcp', ['localhost:5000', 'localhost:5001'])

    registered = plugin.register_tcp()

    assert len(plugin.Plugin.manager.plugins) == 2
    assert isinstance(registered, list)
    assert len(registered) == 2

    assert 'vaporio/test-plugin+tcp@localhost:5000' in registered
    assert 'vaporio/test-plugin+tcp@localhost:5001' in registered

    p = plugin.get_plugin('vaporio/test-plugin+tcp@localhost:5000')
    assert p is not None
    assert p.name == 'test-plugin'
    assert p.protocol == 'tcp'
    assert p.address == 'localhost:5000'

    p = plugin.get_plugin('vaporio/test-plugin+tcp@localhost:5001')
    assert p is not None
    assert p.name == 'test-plugin'
    assert p.protocol == 'tcp'
    assert p.address == 'localhost:5001'


def test_register_tcp_plugin_already_exists(grpc_timeout, mock_client_test_ok, mock_client_meta_ok):
    """Test registering TCP plugin when the plugin was already registered."""
    assert len(plugin.Plugin.manager.plugins) == 0

    config.options.set('plugin.tcp', ['localhost:5000'])

    # register the first time
    registered = plugin.register_tcp()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert isinstance(registered, list)
    assert len(registered) == 1

    assert 'vaporio/test-plugin+tcp@localhost:5000' in registered

    p = plugin.get_plugin('vaporio/test-plugin+tcp@localhost:5000')
    assert p is not None
    assert p.name == 'test-plugin'
    assert p.protocol == 'tcp'
    assert p.address == 'localhost:5000'

    # register the second time
    registered = plugin.register_tcp()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert isinstance(registered, list)
    assert len(registered) == 1

    assert 'vaporio/test-plugin+tcp@localhost:5000' in registered

    p = plugin.get_plugin('vaporio/test-plugin+tcp@localhost:5000')
    assert p is not None
    assert p.name == 'test-plugin'
    assert p.protocol == 'tcp'
    assert p.address == 'localhost:5000'


def test_register_tcp_plugin_env(grpc_timeout, mock_client_test_ok, mock_client_meta_ok):
    """Test registering TCP based plugin when an environment variable is set"""
    assert len(plugin.Plugin.manager.plugins) == 0

    os.environ['SYNSE_PLUGIN_TCP'] = 'localhost:5000'
    config.options.parse()

    registered = plugin.register_tcp()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert isinstance(registered, list)
    assert len(registered) == 1

    assert 'vaporio/test-plugin+tcp@localhost:5000' in registered

    p = plugin.get_plugin('vaporio/test-plugin+tcp@localhost:5000')
    assert p is not None
    assert p.name == 'test-plugin'
    assert p.protocol == 'tcp'
    assert p.address == 'localhost:5000'


def test_register_tcp_plugins_env(grpc_timeout, mock_client_test_ok, mock_client_meta_ok):
    """Test registering TCP based plugins when multiple environment variables are specified"""
    assert len(plugin.Plugin.manager.plugins) == 0

    os.environ['SYNSE_PLUGIN_TCP'] = 'localhost:5000,localhost:5001'
    config.options.parse()

    registered = plugin.register_tcp()

    assert len(plugin.Plugin.manager.plugins) == 2
    assert isinstance(registered, list)
    assert len(registered) == 2

    assert 'vaporio/test-plugin+tcp@localhost:5000' in registered
    assert 'vaporio/test-plugin+tcp@localhost:5001' in registered

    p = plugin.get_plugin('vaporio/test-plugin+tcp@localhost:5000')
    assert p is not None
    assert p.name == 'test-plugin'
    assert p.protocol == 'tcp'
    assert p.address == 'localhost:5000'

    p = plugin.get_plugin('vaporio/test-plugin+tcp@localhost:5001')
    assert p is not None
    assert p.name == 'test-plugin'
    assert p.protocol == 'tcp'
    assert p.address == 'localhost:5001'
