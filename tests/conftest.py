"""Test configuration for Synse Server for all tests.
"""

import logging

import pytest

from synse import config, factory

_app = None


@pytest.fixture(scope='session')
def app():
    """Fixture to get a Synse Server application instance."""
    global _app
    if _app is None:
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
    config.options['pretty_json'] = False


@pytest.fixture(autouse=True)
def i18n_passthrough():
    """Sets i18n.trans_func, just like if i18n.init_gettext was called."""
    from synse import i18n
    old_trans_func = i18n.trans_func
    i18n.old_trans_func = old_trans_func
    trans = lambda s: s
    i18n.trans_func = trans

    yield

    i18n.trans_func = old_trans_func
