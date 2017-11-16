"""Test the 'synse.plugin' Synse Server module."""
# pylint: disable=redefined-outer-name,unused-argument

import os
import shutil
import socket

import pytest

from synse import const, plugin


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
        sock='tmp/test-plug'
    )

    yield p

    sock.shutdown(2)
    sock.close()
    try:
        os.unlink('tmp/test-plug')
    except OSError:
        if os.path.exists('tmp/test-plug'):
            raise


@pytest.fixture(scope='module')
def remove_tmp_dir():
    """Fixture to remove any test data."""
    if os.path.isdir('tmp'):
        shutil.rmtree('tmp')


@pytest.fixture()
def make_bgsocks():
    """Fixture to create and remove the BG_SOCKS directory for testing."""
    if not os.path.isdir(const.BG_SOCKS):
        os.makedirs(const.BG_SOCKS)

    yield

    if os.path.isdir(const.BG_SOCKS):
        shutil.rmtree(const.BG_SOCKS)


@pytest.fixture()
def cleanup(remove_tmp_dir):
    """Fixture to reset the PluginManager state between tests."""
    yield
    plugin.Plugin.manager.plugins = {}


def test_plugin_manager_get(cleanup):
    """Get a plugin from the Manager."""

    pm = plugin.PluginManager()
    pm.plugins['test'] = 'foo'
    assert pm.get('test') == 'foo'


def test_plugin_manager_get_no_value(cleanup):
    """Get a plugin that is not managed by the Manager."""

    pm = plugin.PluginManager()
    assert pm.get('test') is None


def test_plugin_manager_add_invalid(cleanup):
    """Add an invalid plugin."""

    pm = plugin.PluginManager()
    with pytest.raises(ValueError):
        pm.add('plugin')


def test_plugin_manager_add_already_exists(mock_plugin, cleanup):
    """Add a plugin that is already managed by the Manager."""

    pm = plugin.PluginManager()
    pm.plugins['test-plug'] = 'foo'
    with pytest.raises(ValueError):
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

    with pytest.raises(ValueError):
        plugin.Plugin('test', 'some/nonexistent/path')


def test_plugin_ok(cleanup):
    """Create a plugin successfully"""

    if not os.path.isdir('tmp'):
        os.mkdir('tmp')

    # create a file in the tmp dir for the test
    open('tmp/test', 'w').close()

    p = plugin.Plugin('test', 'tmp/test')

    assert p.name == 'test'
    assert p.sock == 'tmp/test'
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
    assert p.sock == 'tmp/test-plug'


def test_get_plugins1(cleanup):
    """Get all plugins when no plugins exist."""

    with pytest.raises(StopIteration):
        next(plugin.get_plugins())


def test_get_plugins2(mock_plugin, cleanup):
    """Get all plugins when some plugins exist."""

    name, p = next(plugin.get_plugins())
    assert isinstance(p, plugin.Plugin)
    assert name == p.name == 'test-plug'
    assert p.sock == 'tmp/test-plug'

    name, p = next(plugin.get_plugins())
    print('NAME P')
    print(name)
    print(p)


def test_register_plugins_no_sock_path(make_bgsocks, cleanup):
    """Register plugins when the plugin path doesn't exist."""

    if os.path.isdir(const.BG_SOCKS):
        shutil.rmtree(const.BG_SOCKS)

    with pytest.raises(ValueError):
        plugin.register_plugins()


def test_register_plugins_no_socks(make_bgsocks, cleanup):
    """Register plugins when no sockets are in the plugin path."""

    # create a non-socket file in the plugin path
    path = os.path.join(const.BG_SOCKS, 'test.txt')
    open(path, 'w').close()

    assert len(plugin.Plugin.manager.plugins) == 0

    plugin.register_plugins()

    assert len(plugin.Plugin.manager.plugins) == 0

    os.unlink(path)


def test_register_plugins_ok(make_bgsocks, cleanup):
    """Register plugins successfully."""

    # create the socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path = '{}/test'.format(const.BG_SOCKS)
    sock.bind(path)

    assert len(plugin.Plugin.manager.plugins) == 0

    plugin.register_plugins()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert 'test' in plugin.Plugin.manager.plugins

    p = plugin.Plugin.manager.plugins['test']
    assert p.name == 'test'
    assert p.sock == path

    try:
        os.unlink(path)
    except OSError:
        if os.path.exists(path):
            raise


def test_register_plugins_already_exists(make_bgsocks, cleanup):
    """Register plugins when the plugins were already registered."""

    # create the socket
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path = '{}/test'.format(const.BG_SOCKS)
    sock.bind(path)

    assert len(plugin.Plugin.manager.plugins) == 0

    plugin.register_plugins()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert 'test' in plugin.Plugin.manager.plugins

    p = plugin.Plugin.manager.plugins['test']
    assert p.name == 'test'
    assert p.sock == path

    # now, re-register
    assert len(plugin.Plugin.manager.plugins) == 1

    plugin.register_plugins()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert 'test' in plugin.Plugin.manager.plugins

    p = plugin.Plugin.manager.plugins['test']
    assert p.name == 'test'
    assert p.sock == path

    try:
        os.unlink(path)
    except OSError:
        if os.path.exists(path):
            raise


def test_register_plugins_new(make_bgsocks, cleanup):
    """Re-register, adding a new plugin."""

    # create the socket
    sock1 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path1 = '{}/foo'.format(const.BG_SOCKS)
    sock1.bind(path1)

    assert len(plugin.Plugin.manager.plugins) == 0

    plugin.register_plugins()

    assert len(plugin.Plugin.manager.plugins) == 1
    assert 'foo' in plugin.Plugin.manager.plugins

    p = plugin.Plugin.manager.plugins['foo']
    assert p.name == 'foo'
    assert p.sock == path1

    # now, re-register
    sock2 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path2 = '{}/bar'.format(const.BG_SOCKS)
    sock2.bind(path2)

    assert len(plugin.Plugin.manager.plugins) == 1

    plugin.register_plugins()

    assert len(plugin.Plugin.manager.plugins) == 2
    assert 'foo' in plugin.Plugin.manager.plugins
    assert 'bar' in plugin.Plugin.manager.plugins

    p = plugin.Plugin.manager.plugins['foo']
    assert p.name == 'foo'
    assert p.sock == path1

    p = plugin.Plugin.manager.plugins['bar']
    assert p.name == 'bar'
    assert p.sock == path2

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
    path1 = '{}/foo'.format(const.BG_SOCKS)
    sock1.bind(path1)

    sock2 = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    path2 = '{}/bar'.format(const.BG_SOCKS)
    sock2.bind(path2)

    assert len(plugin.Plugin.manager.plugins) == 0

    plugin.register_plugins()

    assert len(plugin.Plugin.manager.plugins) == 2
    assert 'foo' in plugin.Plugin.manager.plugins

    p = plugin.Plugin.manager.plugins['foo']
    assert p.name == 'foo'
    assert p.sock == path1

    p = plugin.Plugin.manager.plugins['bar']
    assert p.name == 'bar'
    assert p.sock == path2

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
    assert p.sock == path2

    try:
        os.unlink(path2)
    except OSError:
        if os.path.exists(path2):
            raise
