
import datetime

import pytest

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
