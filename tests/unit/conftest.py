
import datetime

import pytest

from synse_server import plugin, utils

TEST_DATETIME = datetime.datetime(2019, 4, 19, 2, 1, 53, 680718)


@pytest.fixture()
def patch_datetime_utcnow(monkeypatch):
    """Fixture to patch datetime.datetime.utcnow so we have determinable timestamps.

    This must be done as a monkeypatched fixture as opposed to mocking since we
    cannot mock built-in/extension types.
    """

    class patcheddatetime:
        @classmethod
        def utcnow(cls):
            return TEST_DATETIME

    monkeypatch.setattr(datetime, 'datetime', patcheddatetime)


@pytest.fixture()
def clear_manager_plugins():
    yield
    plugin.PluginManager.plugins = {}


@pytest.fixture()
def patch_utils_rfc3339now(monkeypatch):
    """Fixture to patch synse_server.utils.rfc3339now to return a well-known
    timestamp value for testing.
    """

    def patchedrfc3339now():
        return '2019-04-19T02:01:53Z'

    monkeypatch.setattr(utils, 'rfc3339now', patchedrfc3339now)
