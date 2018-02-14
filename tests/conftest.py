"""Test configuration for Synse Server.
"""

import logging
import os
import shutil

import pytest

from synse import const


@pytest.fixture(autouse=True)
def i18n_passthrough():
    """Sets i18n.trans_func, just like if i18n.init_gettext was called.
        If you encounter the following error, you need to include this fixture.

    ```
def gettext(text):
    if trans_func:
        return trans_func(text)
    else:
        raise RuntimeError(
>               'i18n.gettext() not yet initialized, i18n.init_gettext() mus be called first.'
                )
E       RuntimeError: i18n.gettext() not yet initialized, i18n.init_gettext() mus be called first.

synse/i18n.py:62: RuntimeError
    ```
    """
    from synse import i18n
    old_trans_func = i18n.trans_func
    i18n.old_trans_func = old_trans_func
    trans = lambda s: s
    i18n.trans_func = trans

    yield

    i18n.trans_func = old_trans_func


@pytest.fixture()
def plugin_dir():
    """Fixture to setup and teardown the test context for creating plugins."""
    # create paths that will be used by the plugins

    if not os.path.isdir(const.SOCKET_DIR):
        os.makedirs(const.SOCKET_DIR)

    yield

    # cleanup
    if os.path.isdir(const.SOCKET_DIR):
        shutil.rmtree(const.SOCKET_DIR)


@pytest.fixture(autouse=True)
def disable_synse_logging():
    """Disable the synse logger. Negative tests cases will cause
    warning and error level messages to be logged out which can
    make the test output confusing.
    """
    l = logging.getLogger('synse')
    l.disabled = True
