
import datetime

import pytest
from synse_grpc import api, client

from synse_server import cache, plugin, utils

TEST_DATETIME = datetime.datetime(2019, 4, 19, 2, 1, 53, 680718)


# Behavioral Fixtures
# ===================
# These fixtures modify the behavior (e.g. setup / teardown / cleanup actions,
# mocking / patching, etc) of tests/test environments. They do not return anything
# that is usable by the test itself. It is preferable to apply these to test cases
# or test classes via fixture, e.g.
#
#   @pytest.mark.usefixtures(<FIXTURE NAME>)

@pytest.fixture()
def patch_datetime_utcnow(monkeypatch):
    """Fixture to patch ``datetime.datetime.utcnow`` so we have determinable timestamps.

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
    """Fixture to clear the ``synse_server.plugin.PluginManager`` plugins state."""

    yield
    plugin.PluginManager.plugins = {}


@pytest.fixture()
def patch_utils_rfc3339now(monkeypatch):
    """Fixture to patch ``synse_server.utils.rfc3339now`` to return a well-known
    timestamp value for testing.
    """

    def patchedrfc3339now():
        return '2019-04-22T13:30:00Z'

    monkeypatch.setattr(utils, 'rfc3339now', patchedrfc3339now)


@pytest.fixture()
async def clear_txn_cache():
    """Fixture to clear the transaction cache after a test completes."""

    yield
    await cache.device_cache.clear(
        namespace=cache.NS_TRANSACTION,
    )


@pytest.fixture()
async def clear_device_cache():
    """Fixture to clear the device cache after a test completes."""

    yield
    await cache.device_cache.clear(
        namespace=cache.NS_DEVICE,
    )


# Data Fixtures
# =============
# These fixtures provide common test data that can be used for a wide array
# of tests. Fixtures here should be general enough so they can be used by any
# test case that needs them -- not just one or two specific test cases. These
# fixtures return a value, so they should be passed to the test function as
# an argument, e.g.
#
#    def test_something(<FIXTURE NAME>):
#        ...

@pytest.fixture()
def simple_plugin():
    """Fixture to return a new ``synse_server.plugin.Plugin`` instance
    configured minimally.
    """

    return plugin.Plugin(
        client=client.PluginClientV3('localhost:5432', 'tcp'),
        info={
            'tag': 'test/foo',
            'id': '123',
            'vcs': 'https://github.com/vapor-ware/synse-server',
        },
        version={},
    )


@pytest.fixture()
def simple_device():
    """Fixture to return a new ``synse_grpc.api.V3Device`` instance for testing."""

    return api.V3Device(
        timestamp='2019-04-22T13:30:00Z',
        id='test-device-1',
        type='temperature',
        plugin='123',
        info='device for unit tests',
        metadata={
            'foo': 'bar',
        },
        capabilities=api.V3DeviceCapability(
            mode='r',
        ),
        tags=[
            api.V3Tag(
                namespace='vapor',
                annotation='unit',
                label='test',
            ),
        ],
        outputs=[
            api.V3DeviceOutput(
                name='temperature',
                type='temperature',
                precision=3,
                scalingFactor=1,
                unit=api.V3OutputUnit(
                    name='celsius',
                    symbol='C',
                ),
            ),
        ],
        sortIndex=0,
    )


@pytest.fixture()
def temperature_reading():
    """Fixture to return a new V3Reading for a temperature device."""

    return api.V3Reading(
        id='aaa',
        timestamp='2019-04-22T13:30:00Z',
        type='temperature',
        deviceType='temperature',
        context={'zone': '1'},
        unit=api.V3OutputUnit(
            name='celsius',
            symbol='C',
        ),
        int64_value=30,
    )


@pytest.fixture()
def humidity_reading():
    """Fixture to return a new V3Reading for a humidity device."""

    return api.V3Reading(
        id='bbb',
        timestamp='2019-04-22T13:30:00Z',
        type='humidity',
        deviceType='humidity',
        unit=api.V3OutputUnit(
            name='percent',
            symbol='%',
        ),
        float64_value=42.0,
    )


@pytest.fixture()
def state_reading():
    """Fixture to return a new V3Reading for a state device."""

    return api.V3Reading(
        id='ccc',
        timestamp='2019-04-22T13:30:00Z',
        type='state',
        deviceType='led',
        string_value='on',
    )
