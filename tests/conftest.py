"""Test configuration for Synse Server for all tests."""

import logging
import os

import pytest
import yaml

from synse import config, const, factory

_app = None


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
