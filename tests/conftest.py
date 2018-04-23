"""Test configuration for Synse Server for all tests."""

import gettext
import logging
import os
import shutil

import pytest
import yaml

from synse import config, const, factory, i18n
from tests import data_dir

_app = None


@pytest.fixture(scope='session')
def app():
    """Fixture to get a Synse Server application instance."""
    global _app

    # override the default config directory location for testing. this is
    # to prevent collision with anything in the local default socket directory,
    # which could be the case if you are running plugins locally directly
    # on the host (e.g. for development)
    const.SOCKET_DIR = os.path.join(data_dir, 'socks')

    # if the app doesn't exist, create it
    if _app is None:
        with open(os.path.join(data_dir, 'config.yml'), 'w') as f:
            yaml.dump({'log': 'debug'}, f)
        config.options.add_config_paths(data_dir)
        _app = factory.make_app()
    return _app


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
def disable_logging():
    """The loggers. This makes test output much cleaner/easier to read."""
    logging.getLogger('synse').disabled = True
    logging.getLogger('root').disabled = True
    logging.getLogger('sanic.access').disabled = True


@pytest.fixture()
def no_pretty_json():
    """Fixture to ensure basic JSON responses."""
    config.options.set('pretty_json', False)
