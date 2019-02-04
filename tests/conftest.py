"""Test configuration for Synse Server for all tests."""

import logging
import os
import shutil
import socket

import pytest
import yaml

from synse_server import config, const, factory

_app = None


class SocketManager:
    """SocketManager is a helper class for creating, managing, and destroying
    temporary sockets for testing.
    """

    def __init__(self, base_path):
        self.base_path = base_path
        self.socket_dir = os.path.join(self.base_path, 'socks')

        self._old_socket_path = const.SOCKET_DIR
        os.mkdir(self.socket_dir)
        const.SOCKET_DIR = self.socket_dir

    def __del__(self):
        const.SOCKET_DIR = self._old_socket_path
        shutil.rmtree(self.socket_dir)

    def add(self, name):
        """Create a new socket in the socket path."""
        path = os.path.join(self.socket_dir, name)
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(path)
        return sock, path


@pytest.fixture()
def app(tmpdir):
    """Fixture to get a Synse Server application instance."""
    global _app

    appdir = tmpdir.mkdir('appdata')

    # override the default config directory location for testing. this is
    # to prevent collision with anything in the local default socket directory,
    # which could be the case if you are running plugins locally directly
    # on the host (e.g. for development)
    const.SOCKET_DIR = os.path.join(appdir, 'socks')

    # if the app doesn't exist, create it
    if _app is None:
        with open(os.path.join(appdir, 'config.yml'), 'w') as f:
            yaml.dump({'log': 'debug'}, f)
        config.options.add_config_paths(appdir)
        _app = factory.make_app()
    return _app


@pytest.fixture()
def tmpsocket():
    """Fixture that can be used to generate and manage test unix socket data.

    This should be used for all tests that need to set up a unix socket for
    plugin testing. Pytest's tmpdir fixture generally will create temporary
    directories with long path names, but socket paths are character bound,
    so that can lead to test errors.

    The socket test data here is all stored in the `tests/testdata` directory.
    """
    yield SocketManager('tests/testdata')


@pytest.fixture(autouse=True)
def disable_logging():
    """The loggers. This makes test output much cleaner/easier to read."""
    logging.getLogger('synse').disabled = True
    logging.getLogger('root').disabled = True
    logging.getLogger('sanic.access').disabled = True


@pytest.fixture()
def no_pretty_json():
    """Fixture to ensure basic JSON responses."""
    config.options.set('pretty_json', False)
