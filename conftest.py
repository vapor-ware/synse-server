"""Test configuration for Synse Server.
"""

import pytest

# https://stackoverflow.com/a/48207909/5843840
@pytest.fixture(scope='session', autouse=True)
def install_gettext():
    """Adds 'gettext()' to builtins for tests.
    """
    import gettext as g
    trans = g.translation('foo', 'locale', fallback=True)
    trans.install('gettext')
