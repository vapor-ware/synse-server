"""Test configuration for Synse Server.
"""

import pytest
import os

from synse import const, plugin

# https://stackoverflow.com/a/48207909/5843840
@pytest.fixture(scope='session', autouse=True)
def install_gettext():
    """Adds 'gettext()' to builtins for tests.
    """
    import gettext as g
    trans = g.translation('foo', 'locale', fallback=True)
    trans.install('gettext')


@pytest.fixture(scope='session', autouse=True)
def plugin_context():
    """Fixture to setup and teardown the test context for creating plugins."""
    # create paths that will be used by the plugins

    print(const.BG_SOCKS)
    if not os.path.isdir(const.BG_SOCKS):
        os.makedirs(const.BG_SOCKS)

    if not os.path.isdir('tmp'):
        os.mkdir('tmp')

    # create dummy 'socket' files for the plugins
    open('tmp/foo', 'w').close()
    open('tmp/bar', 'w').close()

    yield

    # cleanup
    plugin.Plugin.manager.plugins = {}

    if os.path.isdir('tmp'):
        shutil.rmtree('tmp')

    if os.path.isdir(const.BG_SOCKS):
        shutil.rmtree(const.BG_SOCKS)
