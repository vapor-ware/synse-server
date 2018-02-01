"""Test configuration for Synse Server.
"""

import logging
import os
import shutil

import pytest

from synse import const


# https://stackoverflow.com/a/48207909/5843840
@pytest.fixture(scope='session', autouse=True)
def install_gettext():
    """Adds 'gettext()' to builtins for tests.
    """
    import gettext as g
    trans = g.translation('foo', 'locale', fallback=True)
    trans.install('gettext')


@pytest.fixture()
def plugin_dir():
    """Fixture to setup and teardown the test context for creating plugins."""
    # create paths that will be used by the plugins

    if not os.path.isdir(const.BG_SOCKS):
        os.makedirs(const.BG_SOCKS)

    yield

    # cleanup
    if os.path.isdir(const.BG_SOCKS):
        shutil.rmtree(const.BG_SOCKS)


@pytest.fixture(autouse=True)
def disable_synse_logging():
    """Disable the synse logger. Negative tests cases will cause
    warning and error level messages to be logged out which can
    make the test output confusing.
    """
    l = logging.getLogger('synse')
    l.disabled = True
