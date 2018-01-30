"""Test configuration for Synse Server.
"""

import logging

import pytest


# https://stackoverflow.com/a/48207909/5843840
@pytest.fixture(scope='session', autouse=True)
def install_gettext():
    """Adds 'gettext()' to builtins for tests.
    """
    import gettext as g
    trans = g.translation('foo', 'locale', fallback=True)
    trans.install('gettext')


@pytest.fixture(autouse=True)
def disable_synse_logging():
    """Disable the synse logger. Negative tests cases will cause
    warning and error level messages to be logged out which can
    make the test output confusing.
    """
    l = logging.getLogger('synse')
    l.disabled = True
