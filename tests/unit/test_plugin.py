"""Test the 'synse.plugin' Synse Server module."""
# pylint: disable=redefined-outer-name,unused-argument

import os
import shutil
import socket

import pytest

from synse import config, const, errors, plugin


@pytest.fixture()
def mock_plugin():
    """Convenience fixture to create a test plugin. We create a TCP
    based plugin for ease of testing.
    """
    p = plugin.Plugin(
        name='test-plug',
        address='localhost:9999',
        mode='tcp'
    )

    yield p


@pytest.fixture(scope='module')
def remove_tmp_dir():
    """Fixture to remove any test data."""
    if os.path.isdir('tmp'):
        shutil.rmtree('tmp')


@pytest.fixture()
def make_bgsocks():
    """Fixture to create and remove the BG_SOCKS directory for testing."""
    if not os.path.isdir(const.SOCKET_DIR):
        os.makedirs(const.SOCKET_DIR)

    yield

    if os.path.isdir(const.SOCKET_DIR):
        shutil.rmtree(const.SOCKET_DIR)


@pytest.fixture()
def cleanup(remove_tmp_dir):
    """Fixture to reset the PluginManager state between tests."""
    yield
    plugin.Plugin.manager.plugins = {}


@pytest.fixture()
def clear_config():
    """Reset configuration options to an empty dictionary"""
    yield
    config.options = {}


@pytest.fixture()
def clear_environ():
    """Remove test data put in environment variables."""
    yield
    for k, _ in os.environ.items():
        if k.startswith('SYNSE_PLUGIN_'):
            del os.environ[k]


def test_plugin_manager_get(cleanup):
    """Get a value from the Plugin Manager."""
    pm = plugin.PluginManager()
    pm.plugins['test'] = 'foo'
    assert pm.get('test') == 'foo'


def test_plugin_manager_get_no_value(cleanup):
    """Get a plugin that is not managed by the Manager."""
    pm = plugin.PluginManager()
    assert pm.get('test') is None


def test_plugin_manager_add_invalid(cleanup):
    """Add an invalid plugin (a string is not a valid plugin)."""
    pm = plugin.PluginManager()
    with pytest.raises(errors.PluginStateError):
        pm.add('plugin')


def test_plugin_manager_add_already_exists(mock_plugin, cleanup):
    """Add a plugin that is already managed by the Manager."""
    pm = plugin.PluginManager()
    pm.plugins['test-plug'] = 'foo'
    with pytest.raises(errors.PluginStateError):
        pm.add(mock_plugin)


def test_plugin_manager_add(mock_plugin, cleanup):
    """Add a plugin to the Manager."""
    pm = plugin.PluginManager()
    assert len(pm.plugins) == 0
    pm.add(mock_plugin)
    assert len(pm.plugins) == 1
    assert 'test-plug' in pm.plugins


def test_plugin_manager_remove(mock_plugin, cleanup):
    """Remove a plugin from the Manager."""
    pm = plugin.PluginManager()
    pm.plugins['test-plug'] = mock_plugin
    assert len(pm.plugins) == 1
    assert 'test-plug' in pm.plugins

    pm.remove('test-plug')
    assert len(pm.plugins) == 0
    assert 'test-plug' not in pm.plugins


def test_plugin_manager_remove_nonexistent(cleanup):
    """Remove a plugin from the Manager that is not there."""
    pm = plugin.PluginManager()
    assert len(pm.plugins) == 0
    pm.remove('test')
    assert len(pm.plugins) == 0


def test_plugin_path_not_exist(cleanup):
    """Create a plugin when the socket doesn't exist."""
    with pytest.raises(errors.PluginStateError):
        plugin.Plugin('test', 'some/nonexistent/path', 'unix')


def test_plugin_invalid_mode(cleanup):
    """Create a plugin when the mode is invalid."""
    with pytest.raises(errors.PluginStateError):
        plugin.Plugin('test', 'some/addr', 'foo')


def test_plugin_ok(cleanup):
    """Create a plugin successfully"""
    if not os.path.isdir('tmp'):
        os.mkdir('tmp')

    # create a file in the tmp dir for the test
    open('tmp/test', 'w').close()

    p = plugin.Plugin('test', 'tmp/test', 'unix')

    assert p.name == 'test'
    assert p.addr == 'tmp/test'
    assert p.mode == 'unix'
    assert p.client is not None

    try:
        os.unlink('tmp/test')
    except OSError:
        if os.path.exists('tmp/test'):
            raise


def test_plugins_same_manager(mock_plugin, cleanup):
    """Check that all plugins have the same manager."""
    assert plugin.Plugin.manager == mock_plugin.manager


def test_get_plugin1(cleanup):
    """Get a plugin when it doesn't exist."""
    p = plugin.get_plugin('test')
    assert p is None


def test_get_plugin2(mock_plugin, cleanup):
    """Get a plugin when it does exist."""
    p = plugin.get_plugin('test-plug')
    assert isinstance(p, plugin.Plugin)
    assert p.name == 'test-plug'
    assert p.addr == 'localhost:9999'
    assert p.mode == 'tcp'


@pytest.mark.asyncio
async def test_get_plugins1(cleanup):
    """Get all plugins when no plugins exist."""
    with pytest.raises(StopAsyncIteration):
        await plugin.get_plugins().__anext__()


@pytest.mark.asyncio
async def test_get_plugins2(mock_plugin, cleanup):
    """Get all plugins when some plugins exist."""
    name, p = await plugin.get_plugins().__anext__()
    assert isinstance(p, plugin.Plugin)
    assert name == p.name == 'test-plug'
    assert p.addr == 'localhost:9999'
    assert p.mode == 'tcp'


def test_register_plugins_no_sock_path(make_bgsocks, cleanup):
    """Register plugins when the plugin path doesn't exist."""
    if os.path.isdir(const.SOCKET_DIR):
        shutil.rmtree(const.SOCKET_DIR)

    assert len(plugin.Plugin.manager.plugins) == 0
    plugin.register_plugins()
    assert len(plugin.Plugin.manager.plugins) == 0


def test_register_plugins_no_socks(make_bgsocks, cleanup):
    """Register plugins when no sockets are in the plugin path."""
    # create a non-socket file in the plugin path
    path = os.path.join(const.SOCKET_DIR, 'test.txt')
    open(path, 'w').close()

    assert len(plugin.Plugin.manager.plugins) == 0

    plugin.register_plugins()

    assert len(plugin.Plugin.manager.plugins) == 0

    os.unlink(path)


def test_register_plugins_ok(make_bgsocks, cleanup):
    """Register plugins successfully."""
    # create the socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path = '{}/test'.format(const.SOCKET_DIR)
    sock.bind(path)

    assert len(plugin.Plugin.manager.plugins) == 0

    plugin.register_plugins()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert 'test' in plugin.Plugin.manager.plugins

    p = plugin.Plugin.manager.plugins['test']
    assert p.name == 'test'
    assert p.addr == path
    assert p.mode == 'unix'

    try:
        os.unlink(path)
    except OSError:
        if os.path.exists(path):
            raise


def test_register_plugins_already_exists(make_bgsocks, cleanup):
    """Register plugins when the plugins were already registered."""
    # create the socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path = '{}/test'.format(const.SOCKET_DIR)
    sock.bind(path)

    assert len(plugin.Plugin.manager.plugins) == 0

    plugin.register_plugins()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert 'test' in plugin.Plugin.manager.plugins

    p = plugin.Plugin.manager.plugins['test']
    assert p.name == 'test'
    assert p.addr == path
    assert p.mode == 'unix'

    # now, re-register
    assert len(plugin.Plugin.manager.plugins) == 1

    plugin.register_plugins()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert 'test' in plugin.Plugin.manager.plugins

    p = plugin.Plugin.manager.plugins['test']
    assert p.name == 'test'
    assert p.addr == path
    assert p.mode == 'unix'

    try:
        os.unlink(path)
    except OSError:
        if os.path.exists(path):
            raise


def test_register_plugins_new(make_bgsocks, cleanup):
    """Re-register, adding a new plugin."""
    # create the socket
    sock1 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path1 = '{}/foo'.format(const.SOCKET_DIR)
    sock1.bind(path1)

    assert len(plugin.Plugin.manager.plugins) == 0

    plugin.register_plugins()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert 'foo' in plugin.Plugin.manager.plugins

    p = plugin.Plugin.manager.plugins['foo']
    assert p.name == 'foo'
    assert p.addr == path1
    assert p.mode == 'unix'

    # now, re-register
    sock2 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path2 = '{}/bar'.format(const.SOCKET_DIR)
    sock2.bind(path2)

    assert len(plugin.Plugin.manager.plugins) == 1

    plugin.register_plugins()

    assert len(plugin.Plugin.manager.plugins) == 2
    assert 'foo' in plugin.Plugin.manager.plugins
    assert 'bar' in plugin.Plugin.manager.plugins

    p = plugin.Plugin.manager.plugins['foo']
    assert p.name == 'foo'
    assert p.addr == path1
    assert p.mode == 'unix'

    p = plugin.Plugin.manager.plugins['bar']
    assert p.name == 'bar'
    assert p.addr == path2
    assert p.mode == 'unix'

    for path in [path1, path2]:
        try:
            os.unlink(path)
        except OSError:
            if os.path.exists(path):
                raise


def test_register_plugins_old(make_bgsocks, cleanup):
    """Re-register, removing an old plugin."""
    # create the socket
    sock1 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path1 = '{}/foo'.format(const.SOCKET_DIR)
    sock1.bind(path1)

    sock2 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path2 = '{}/bar'.format(const.SOCKET_DIR)
    sock2.bind(path2)

    assert len(plugin.Plugin.manager.plugins) == 0

    plugin.register_plugins()

    assert len(plugin.Plugin.manager.plugins) == 2
    assert 'foo' in plugin.Plugin.manager.plugins

    p = plugin.Plugin.manager.plugins['foo']
    assert p.name == 'foo'
    assert p.addr == path1
    assert p.mode == 'unix'

    p = plugin.Plugin.manager.plugins['bar']
    assert p.name == 'bar'
    assert p.addr == path2
    assert p.mode == 'unix'

    # remove one of the sockets and re-register.
    try:
        os.unlink(path1)
    except OSError:
        if os.path.exists(path1):
            raise

    assert len(plugin.Plugin.manager.plugins) == 2

    plugin.register_plugins()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert 'bar' in plugin.Plugin.manager.plugins

    p = plugin.Plugin.manager.plugins['bar']
    assert p.name == 'bar'
    assert p.addr == path2
    assert p.mode == 'unix'

    try:
        os.unlink(path2)
    except OSError:
        if os.path.exists(path2):
            raise


def test_register_unix_plugin_none_defined(cleanup):
    """Test registering unix based plugins when none is specified."""
    assert len(plugin.Plugin.manager.plugins) == 0

    registered = plugin.register_unix_plugins()

    assert len(plugin.Plugin.manager.plugins) == 0
    assert isinstance(registered, list)
    assert len(registered) == 0


def test_register_unix_plugin(cleanup, clear_config):
    """Test registering unix plugin when a configuration is specified"""
    # create the socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path = 'tmp/foo'
    sock.bind(path)

    assert len(plugin.Plugin.manager.plugins) == 0

    # set a configuration
    config.options = {
        'plugin': {
            'unix': {
                'foo': 'tmp'
            }
        }
    }

    registered = plugin.register_unix_plugins()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert isinstance(registered, list)
    assert len(registered) == 1

    assert 'foo' in registered

    p = plugin.get_plugin('foo')
    assert p is not None
    assert p.name == 'foo'
    assert p.mode == 'unix'
    assert p.addr == 'tmp/foo'

    try:
        os.unlink(path)
        shutil.rmtree(path)
    except OSError:
        if os.path.exists(path):
            raise


def test_register_unix_plugins(cleanup, clear_config):
    """Test registering unix plugins when multiple configurations are specified"""
    # create sockets
    sock1 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path1 = 'tmp/foo'
    sock1.bind(path1)

    sock2 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path2 = 'tmp/bar'
    sock2.bind(path2)

    assert len(plugin.Plugin.manager.plugins) == 0

    # set configurations
    config.options = {
        'plugin': {
            'unix': {
                'foo': 'tmp',
                'bar': 'tmp'
            }
        }
    }

    registered = plugin.register_unix_plugins()

    assert len(plugin.Plugin.manager.plugins) == 2
    assert isinstance(registered, list)
    assert len(registered) == 2

    assert 'foo' in registered
    assert 'bar' in registered

    p1 = plugin.get_plugin('foo')
    assert p1 is not None
    assert p1.name == 'foo'
    assert p1.mode == 'unix'
    assert p1.addr == 'tmp/foo'

    p2 = plugin.get_plugin('bar')
    assert p2 is not None
    assert p2.name == 'bar'
    assert p2.mode == 'unix'
    assert p2.addr == 'tmp/bar'

    try:
        os.unlink(path1)
        os.unlink(path2)
        shutil.rmtree(path1)
        shutil.rmtree(path2)
    except OSError:
        if os.path.exists(path1):
            raise
        elif os.path.exists(path2):
            raise


def test_register_unix_plugin_already_exists(make_bgsocks, cleanup):
    """Test registering unix plugin when the plugin was already registered."""
    # create the socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path = '{}/test'.format(const.SOCKET_DIR)
    sock.bind(path)

    assert len(plugin.Plugin.manager.plugins) == 0

    registered = plugin.register_unix_plugins()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert isinstance(registered, list)
    assert len(registered) == 1

    assert 'test' in registered

    p = plugin.get_plugin('test')
    assert p is not None
    assert p.name == 'test'
    assert p.addr == path
    assert p.mode == 'unix'

    # now, re-register
    assert len(plugin.Plugin.manager.plugins) == 1

    # set the same configuration
    config.options = {
        'plugin': {
            'unix': {
                'test': '{}'.format(const.SOCKET_DIR),
            }
        }
    }

    registered = plugin.register_unix_plugins()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert isinstance(registered, list)
    assert len(registered) == 1

    assert 'test' in registered

    p = plugin.get_plugin('test')
    assert p is not None
    assert p.name == 'test'
    assert p.addr == path
    assert p.mode == 'unix'

    try:
        os.unlink(path)
    except OSError:
        if os.path.exists(path):
            raise


def test_register_unix_plugin_no_socket():
    """Test registering unix plugin when no socket is bind"""
    # create a temporary path
    if not os.path.isdir('tmp/foo'):
        os.makedirs('tmp/foo')

    assert len(plugin.Plugin.manager.plugins) == 0

    config.options = {
        'plugin': {
            'unix': {
                'foo': 'tmp'
            }
        }
    }

    registered = plugin.register_unix_plugins()

    assert len(plugin.Plugin.manager.plugins) == 0
    assert isinstance(registered, list)
    assert len(registered) == 0

    shutil.rmtree('tmp/foo')


def test_register_unix_plugin_no_socket_no_path():
    """Test registering unix plugin when no socket is bind, no path is available"""
    assert len(plugin.Plugin.manager.plugins) == 0

    config.options = {
        'plugin': {
            'unix': {
                'foo': 'tmp'
            }
        }
    }

    registered = plugin.register_unix_plugins()

    assert len(plugin.Plugin.manager.plugins) == 0
    assert isinstance(registered, list)
    assert len(registered) == 0


def test_register_unix_plugin_no_config_path(make_bgsocks, cleanup):
    """Test registering unix plugin when a configuration without a path is specified"""
    # create the socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path = '{}/foo'.format(const.SOCKET_DIR)
    sock.bind(path)

    assert len(plugin.Plugin.manager.plugins) == 0

    config.options = {
        'plugin': {
            'unix': {
                'foo': None
            }
        }
    }

    registered = plugin.register_unix_plugins()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert isinstance(registered, list)
    assert len(registered) == 1

    assert 'foo' in registered

    p = plugin.get_plugin('foo')
    assert p is not None
    assert p.name == 'foo'
    assert p.mode == 'unix'
    assert p.addr == '{}/foo'.format(const.SOCKET_DIR)

    try:
        os.unlink(path)
        shutil.rmtree(path)
    except OSError:
        if os.path.exists(path):
            raise


def test_register_tcp_plugin_none_defined(cleanup):
    """Test registering TCP based plugins when none is specified."""
    assert len(plugin.Plugin.manager.plugins) == 0

    registered = plugin.register_tcp_plugins()

    assert len(plugin.Plugin.manager.plugins) == 0
    assert isinstance(registered, list)
    assert len(registered) == 0


def test_register_tcp_plugin(cleanup, clear_config):
    """Test registering TCP based plugin when a configuration is specified"""
    assert len(plugin.Plugin.manager.plugins) == 0

    config.options = {
        'plugin': {
            'tcp': {
                'foo': 'localhost:5000'
            }
        }
    }

    registered = plugin.register_tcp_plugins()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert isinstance(registered, list)
    assert len(registered) == 1

    assert 'foo' in registered

    p = plugin.get_plugin('foo')
    assert p is not None
    assert p.name == 'foo'
    assert p.mode == 'tcp'
    assert p.addr == 'localhost:5000'


def test_register_tcp_plugins(cleanup, clear_config):
    """Test registering TCP based plugins when multiple configurations are specified"""
    assert len(plugin.Plugin.manager.plugins) == 0

    config.options = {
        'plugin': {
            'tcp': {
                'foo': 'localhost:5000',
                'bar': 'localhost:5001',
            }
        }
    }

    registered = plugin.register_tcp_plugins()

    assert len(plugin.Plugin.manager.plugins) == 2
    assert isinstance(registered, list)
    assert len(registered) == 2

    assert 'foo' in registered
    assert 'bar' in registered

    p = plugin.get_plugin('foo')
    assert p is not None
    assert p.name == 'foo'
    assert p.mode == 'tcp'
    assert p.addr == 'localhost:5000'

    p = plugin.get_plugin('bar')
    assert p is not None
    assert p.name == 'bar'
    assert p.mode == 'tcp'
    assert p.addr == 'localhost:5001'


def test_register_tcp_plugin_already_exists(cleanup, clear_config):
    """Test registering TCP plugin when the plugin was already registered."""
    assert len(plugin.Plugin.manager.plugins) == 0

    config.options = {
        'plugin': {
            'tcp': {
                'foo': 'localhost:5000'
            }
        }
    }

    # register the first time
    registered = plugin.register_tcp_plugins()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert isinstance(registered, list)
    assert len(registered) == 1

    assert 'foo' in registered

    p = plugin.get_plugin('foo')
    assert p is not None
    assert p.name == 'foo'
    assert p.mode == 'tcp'
    assert p.addr == 'localhost:5000'

    # register the second time
    registered = plugin.register_tcp_plugins()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert isinstance(registered, list)
    assert len(registered) == 1

    assert 'foo' in registered

    p = plugin.get_plugin('foo')
    assert p is not None
    assert p.name == 'foo'
    assert p.mode == 'tcp'
    assert p.addr == 'localhost:5000'


def test_register_tcp_plugin_env(cleanup, clear_config, clear_environ):
    """Test registering TCP based plugin when an environment variable is set"""
    assert len(plugin.Plugin.manager.plugins) == 0

    os.environ['SYNSE_PLUGIN_TCP_FOO'] = 'localhost:5000'
    config.parse_env_vars()

    registered = plugin.register_tcp_plugins()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert isinstance(registered, list)
    assert len(registered) == 1

    assert 'foo' in registered

    p = plugin.get_plugin('foo')
    assert p is not None
    assert p.name == 'foo'
    assert p.mode == 'tcp'
    assert p.addr == 'localhost:5000'


def test_register_tcp_plugins_env(cleanup, clear_config, clear_environ):
    """Test registering TCP based plugins when multiple environment variables are specified"""
    assert len(plugin.Plugin.manager.plugins) == 0

    os.environ['SYNSE_PLUGIN_TCP_FOO'] = 'localhost:5000'
    os.environ['SYNSE_PLUGIN_TCP_BAR'] = 'localhost:5001'
    config.parse_env_vars()

    registered = plugin.register_tcp_plugins()

    assert len(plugin.Plugin.manager.plugins) == 2
    assert isinstance(registered, list)
    assert len(registered) == 2

    assert 'foo' in registered
    assert 'bar' in registered

    p = plugin.get_plugin('foo')
    assert p is not None
    assert p.name == 'foo'
    assert p.mode == 'tcp'
    assert p.addr == 'localhost:5000'

    p = plugin.get_plugin('bar')
    assert p is not None
    assert p.name == 'bar'
    assert p.mode == 'tcp'
    assert p.addr == 'localhost:5001'


def test_register_tcp_plugin_env_duplicate(cleanup, clear_config, clear_environ):
    """Test registering TCP based plugins when same environment variables are specified."""
    assert len(plugin.Plugin.manager.plugins) == 0

    os.environ['SYNSE_PLUGIN_TCP_FOO'] = 'localhost:5000'
    os.environ['SYNSE_PLUGIN_TCP_FOO'] = 'localhost:5001'
    config.parse_env_vars()

    registered = plugin.register_tcp_plugins()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert isinstance(registered, list)
    assert len(registered) == 1

    assert 'foo' in registered

    p = plugin.get_plugin('foo')
    assert p is not None
    assert p.name == 'foo'
    assert p.mode == 'tcp'
    assert p.addr == 'localhost:5001'
