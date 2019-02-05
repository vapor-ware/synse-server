"""Test the 'synse_server.cache' Synse Server module."""
# pylint: disable=redefined-outer-name,unused-argument,line-too-long

import aiocache
import asynctest
import grpc
import pytest
from synse_grpc import api

from synse_server import cache, errors, plugin
from synse_server.proto import client

# -- Helper Methods ---


def make_device_info_response(rack, board, device):
    """Helper method to make a new Device object."""
    return api.Device(
        timestamp='october',
        uid=device,
        kind='thermistor',
        metadata=dict(
            model='test',
            manufacturer='vapor io',
        ),
        plugin='foo',
        info='bar',
        location=api.Location(
            rack=rack,
            board=board
        ),
        output=[
            api.Output(
                type='temperature',
                precision=3,
                unit=api.Unit(
                    name='celsius',
                    symbol='C'
                )
            )
        ]
    )

# --- Mock Methods ---


def mock_get_device_info_cache():
    """Mock method for get_device_info_cache - returns a single device."""
    return {
        'rack-1-vec-12345': make_device_info_response('rack-1', 'vec', '12345')
    }


def mock_client_devices(rack=None, board=None):
    """Mock method for the gRPC client's devices method."""
    # reuse the Device defined above
    mir = mock_get_device_info_cache()['rack-1-vec-12345']
    return [mir]


def mock_client_device_info_empty(rack=None, board=None):
    """Mock method for the gRPC client's Devices method that contains empty Device list."""
    return []


def mock_client_device_info_fail(rack=None, board=None):
    """Mock method for the gRPC client's Devices method that is intended to fail."""
    raise grpc.RpcError()

# --- Test Fixtures ---


@pytest.fixture()
def patch_device_info(monkeypatch):
    """Fixture to monkeypatch the get_device_info_cache method."""
    mock = asynctest.CoroutineMock(cache.get_device_info_cache, side_effect=mock_get_device_info_cache)
    monkeypatch.setattr(cache, 'get_device_info_cache', mock)
    return patch_device_info


@pytest.fixture()
def plugin_context(tmpdir):
    """Fixture to setup and teardown the test context for creating plugins."""

    # create dummy 'socket' files for the plugins
    sockdir = tmpdir.mkdir('socks')
    sockdir.join('foo')
    sockdir.join('bar')


# --- Test Cases ---


def test_configure_cache():
    """Configure the aiocache namespace."""

    assert aiocache.caches._config != cache.AIOCACHE

    cache.configure_cache()

    assert aiocache.caches._config == cache.AIOCACHE
    assert 'default' in aiocache.caches._config


@pytest.mark.asyncio
async def test_clear_cache():
    """Test clearing a cache."""

    test_cache = aiocache.SimpleMemoryCache(namespace='test')

    # first, put a value in the cache and ensure it is there.
    await test_cache.set('key', 'value')
    val = await test_cache.get('key')
    assert val == 'value'

    # clear the cache
    await cache.clear_cache('test')

    val = await test_cache.get('key')
    assert val is None


@pytest.mark.asyncio
async def test_clear_all_meta_caches():
    """Clear all meta-info caches."""

    meta = aiocache.SimpleMemoryCache(namespace=cache.NS_DEVICE_INFO)
    scan = aiocache.SimpleMemoryCache(namespace=cache.NS_SCAN)
    info = aiocache.SimpleMemoryCache(namespace=cache.NS_INFO)
    other = aiocache.SimpleMemoryCache(namespace='other')

    # first, populate the test caches
    for c in [meta, scan, info, other]:
        ok = await c.set('key', 'value')
        assert ok

    # clear the meta caches
    await cache.clear_all_meta_caches()

    # now, the meta caches should be empty, but the other cache
    # should not be affected.
    for c in [meta, scan, info]:
        val = await c.get('key')
        assert val is None

    val = await other.get('key')
    assert val == 'value'


@pytest.mark.asyncio
async def test_get_transaction_ok(clear_caches):
    """Get transaction info from the transaction cache."""

    ok = await cache.transaction_cache.set('key', 'value')
    assert ok

    val = await cache.get_transaction('key')
    assert val == 'value'


@pytest.mark.asyncio
async def test_get_transaction_none(clear_caches):
    """Get transaction info from the transaction cache when the key doesn't exist."""

    val = await cache.get_transaction('test')
    assert val is None


@pytest.mark.asyncio
async def test_add_transaction_new(clear_caches):
    """Add a new value to the transaction cache."""

    pre = await cache.transaction_cache.get('test')
    assert pre is None

    ok = await cache.add_transaction('test', {'action': 'test', 'raw': None}, 'foo')
    assert ok

    post = await cache.transaction_cache.get('test')
    assert post == {
        'plugin': 'foo',
        'context': {
            'action': 'test',
            'raw': None
        }
    }


@pytest.mark.asyncio
async def test_add_transaction_existing(clear_caches):
    """Update an existing value in the transaction cache."""

    pre = await cache.transaction_cache.get('test')
    assert pre is None

    ok = await cache.add_transaction('test', {'action': 'test', 'raw': None}, 'foo')
    assert ok

    post = await cache.transaction_cache.get('test')
    assert post == {
        'plugin': 'foo',
        'context': {
            'action': 'test',
            'raw': None
        }
    }

    ok = await cache.add_transaction('test', {'action': 'test2', 'raw': '1'}, 'foo2')
    assert ok

    post = await cache.transaction_cache.get('test')
    assert post == {
        'plugin': 'foo2',
        'context': {
            'action': 'test2',
            'raw': '1'
        }
    }


@pytest.mark.asyncio
async def test_get_device_meta_ok(patch_device_info, clear_caches):
    """Get device info."""
    # add a plugin record to for the device
    await cache._plugins_cache.set(cache.PLUGINS_CACHE_KEY, {'rack-1-vec-12345': 'test-plugin'})

    plugin_name, dev = await cache.get_device_info('rack-1', 'vec', '12345')
    assert plugin_name == 'test-plugin'
    assert isinstance(dev, api.Device)
    assert dev.uid == '12345'
    assert dev.location.rack == 'rack-1'
    assert dev.location.board == 'vec'


@pytest.mark.asyncio
async def test_get_device_meta_not_found(clear_caches):
    """Get device info when the specified device doesn't exist."""

    with pytest.raises(errors.NotFound):
        await cache.get_device_info('foo', 'bar', 'baz')


@pytest.mark.asyncio
async def test_get_device_info_cache_ok(plugin_context, clear_caches):
    """Get the device info cache."""

    # create & register new plugin
    p = plugin.Plugin(
        metadata=api.Metadata(
            name='foo',
            tag='vaporio/foo'
        ),
        address='localhost:9999',
        plugin_client=client.PluginTCPClient('localhost:9999')
    )
    p.client.devices = mock_client_devices

    meta = await cache.get_device_info_cache()
    assert isinstance(meta, dict)
    assert 'rack-1-vec-12345' in meta
    assert meta['rack-1-vec-12345'] == mock_get_device_info_cache()['rack-1-vec-12345']


@pytest.mark.asyncio
async def test_get_device_info_cache_empty(plugin_context, clear_caches):
    """Get the empty device info cache."""

    # create & register new plugin
    p = plugin.Plugin(
        metadata=api.Metadata(
            name='foo',
            tag='vaporio/foo'
        ),
        address='localhost:9999',
        plugin_client=client.PluginTCPClient('localhost:9999')
    )
    p.client.devices = mock_client_device_info_empty

    meta = await cache.get_device_info_cache()
    assert isinstance(meta, dict)
    assert len(meta) == 0


@pytest.mark.asyncio
async def test_get_device_info_cache_exist(plugin_context, clear_caches):
    """Get the existing device info cache."""

    # create & register new plugin
    p = plugin.Plugin(
        metadata=api.Metadata(
            name='foo',
            tag='vaporio/foo'
        ),
        address='localhost:9999',
        plugin_client=client.PluginTCPClient('localhost:9999')
    )
    p.client.devices = mock_client_devices

    # this is the first time we ask for cache
    # it's not there yet so we build one
    first_meta = await cache.get_device_info_cache()
    assert isinstance(first_meta, dict)
    assert 'rack-1-vec-12345' in first_meta
    assert first_meta['rack-1-vec-12345'] == mock_get_device_info_cache()['rack-1-vec-12345']

    # this is the second time we ask for it
    # it should be there this time and return right away
    second_meta = await cache.get_device_info_cache()
    assert isinstance(second_meta, dict)
    assert 'rack-1-vec-12345' in second_meta
    assert second_meta['rack-1-vec-12345'] == mock_get_device_info_cache()['rack-1-vec-12345']


@pytest.mark.asyncio
async def test_get_device_info_cache_total_failure(plugin_context, clear_caches):
    """Get the device info cache when all plugins fail to respond."""

    # create & register new plugin
    p = plugin.Plugin(
        metadata=api.Metadata(
            name='foo',
            tag='vaporio/foo'
        ),
        address='localhost:9999',
        plugin_client=client.PluginTCPClient('localhost:9999')
    )
    p.client.devices = mock_client_device_info_fail  # override to induce failure

    with pytest.raises(errors.ServerError):
        await cache.get_device_info_cache()


@pytest.mark.asyncio
async def test_get_device_info_cache_partial_failure(plugin_context, clear_caches):
    """Get the device info cache when some plugins fail to respond."""

    # create & register new plugins
    p = plugin.Plugin(
        metadata=api.Metadata(
            name='foo',
            tag='vaporio/foo'
        ),
        address='localhost:9999',
        plugin_client=client.PluginTCPClient('localhost:9999')
    )
    p.client.devices = mock_client_devices

    p = plugin.Plugin(
        metadata=api.Metadata(
            name='bar',
            tag='vaporio/bar'
        ),
        address='localhost:9998',
        plugin_client=client.PluginTCPClient('localhost:9998')
    )
    p.client.devices = mock_client_device_info_fail  # override to induce failure

    meta = await cache.get_device_info_cache()
    assert isinstance(meta, dict)
    assert len(meta) == 1  # two plugins registered, but only one successful


@pytest.mark.asyncio
async def test_get_device_info_cache_no_plugins(clear_caches, plugin_context):
    """Get the device info cache when there are no plugins to provide data."""

    meta = await cache.get_device_info_cache()
    assert meta == {}


@pytest.mark.asyncio
async def test_get_scan_cache_ok(patch_device_info, clear_caches):
    """Get the scan cache."""

    scan_cache = await cache.get_scan_cache()
    validate_scan_cache(scan_cache, 'rack-1', 'vec', '12345')


@pytest.mark.asyncio
async def test_get_scan_cache_empty(plugin_context, clear_caches):
    """Get the empty scan cache."""

    # create & register new plugin with empty device info cache
    p = plugin.Plugin(
        metadata=api.Metadata(
            name='foo',
            tag='vaporio/foo'
        ),
        address='localhost:9999',
        plugin_client=client.PluginTCPClient('localhost:9999')
    )
    p.client.devices = mock_client_device_info_empty

    meta_cache = await cache.get_device_info_cache()
    assert isinstance(meta_cache, dict)
    assert len(meta_cache) == 0

    # because device info cache is empty and scan cache is built upon device info's
    # scan cache should also be empty
    scan_cache = await cache.get_scan_cache()
    assert isinstance(scan_cache, dict)
    assert len(scan_cache) == 0


@pytest.mark.asyncio
async def test_get_scan_cache_exist(patch_device_info, clear_caches):
    """Get the existing scan cache."""

    # similar to test_get_device_info_cache_exist(),
    # the first time we ask for cache, it's not there so we build one
    first_scan_cache = await cache.get_scan_cache()
    validate_scan_cache(first_scan_cache, 'rack-1', 'vec', '12345')

    # the second time we ask for it, it should return right away
    second_scan_cache = await cache.get_scan_cache()
    validate_scan_cache(second_scan_cache, 'rack-1', 'vec', '12345')


@pytest.mark.asyncio
async def test_get_resource_info_cache_ok(patch_device_info, clear_caches):
    """Get the resource info cache."""

    info_cache = await cache.get_resource_info_cache()
    validate_info_cache(info_cache, 'rack-1', 'vec', '12345')


@pytest.mark.asyncio
async def test_get_resource_info_cache_empty(plugin_context, clear_caches):
    """Get the empty info cache."""

    # create & register new plugin with empty device info cache
    p = plugin.Plugin(
        metadata=api.Metadata(
            name='foo',
            tag='vaporio/foo'
        ),
        address='localhost:9999',
        plugin_client=client.PluginTCPClient('localhost:9999')
    )
    p.client.devices = mock_client_device_info_empty

    meta_cache = await cache.get_device_info_cache()
    assert isinstance(meta_cache, dict)
    assert len(meta_cache) == 0

    # because device info cache is empty and info cache is built upon device info's
    # scan cache should also be empty
    info_cache = await cache.get_resource_info_cache()
    assert isinstance(info_cache, dict)
    assert len(info_cache) == 0


@pytest.mark.asyncio
async def test_get_resource_info_cache_exist(patch_device_info, clear_caches):
    """Get the existing info cache."""

    # similar to test_get_device_info_cache_exist(),
    # the first time we ask for cache, it's not there so we build one
    first_info_cache = await cache.get_resource_info_cache()
    validate_info_cache(first_info_cache, 'rack-1', 'vec', '12345')

    # the second time we ask for it, it should return right away
    second_info_cache = await cache.get_resource_info_cache()
    validate_info_cache(second_info_cache, 'rack-1', 'vec', '12345')


def test_build_scan_cache_ok():
    """Build the scan cache."""

    device_info = {
        'rack-1-vec-12345': make_device_info_response('rack-1', 'vec', '12345'),
        'rack-1-board-12345': make_device_info_response('rack-1', 'board', '12345'),
        'rack-1-board-56789': make_device_info_response('rack-1', 'board', '456789'),
        'rack-1-board-abcd': make_device_info_response('rack-1', 'board', 'abcd')
    }
    scan_cache = cache._build_scan_cache(device_info)

    # Test that the scan cache comes back in the expected sorted order
    assert scan_cache == {
        'racks': [
            {
                'id': 'rack-1',
                'boards': [
                    {
                        'id': 'board',
                        'devices': [
                            {
                                'id': '12345',
                                'info': 'bar',
                                'type': 'thermistor'
                            },
                            {
                                'id': '456789',
                                'info': 'bar',
                                'type': 'thermistor'
                            },
                            {
                                'id': 'abcd',
                                'info': 'bar',
                                'type': 'thermistor'
                            },
                        ]
                    },
                    {
                        'id': 'vec',
                        'devices': [
                            {
                                'id': '12345',
                                'info': 'bar',
                                'type': 'thermistor'
                            }
                        ]
                    }
                ]
            }
        ]
    }


def test_build_scan_cache_no_device_info():
    """Build the scan cache when empty device info is provided."""

    device_info = {}
    scan_cache = cache._build_scan_cache(device_info)
    assert scan_cache == {}


def test_build_info_cache_ok():
    """Build the info cache."""

    device_info = {
        'rack-1-vec-12345': make_device_info_response('rack-1', 'vec', '12345'),
        'rack-1-board-12345': make_device_info_response('rack-1', 'board', '12345'),
        'rack-1-board-56789': make_device_info_response('rack-1', 'board', '456789')
    }
    info_cache = cache._build_resource_info_cache(device_info)
    validate_info_cache(info_cache, 'rack-1', 'vec', '12345')
    validate_info_cache(info_cache, 'rack-1', 'board', '12345')
    validate_info_cache(info_cache, 'rack-1', 'board', '456789')


def test_build_info_cache_no_device_info():
    """Build the info cache when empty device info is provided."""

    device_info = {}
    info_cache = cache._build_resource_info_cache(device_info)
    assert info_cache == {}


def validate_scan_cache(scan_cache, expected_rack, expected_board, expected_device):
    """Helper to validate the scan cache."""

    assert isinstance(scan_cache, dict)

    assert 'racks' in scan_cache
    assert isinstance(scan_cache['racks'], list)

    rack = None
    for r in scan_cache['racks']:
        if r['id'] == expected_rack:
            rack = r

    assert rack is not None
    assert 'id' in rack
    assert 'boards' in rack
    assert rack['id'] == expected_rack
    assert isinstance(rack['boards'], list)

    board = None
    for b in rack['boards']:
        if b['id'] == expected_board:
            board = b

    assert board is not None
    assert 'id' in board
    assert 'devices' in board
    assert board['id'] == expected_board
    assert isinstance(board['devices'], list)

    device = None
    for d in board['devices']:
        if d['id'] == expected_device:
            device = d

    assert device is not None
    assert 'id' in device
    assert device['id'] == expected_device
    assert 'info' in device
    assert 'type' in device


def validate_info_cache(info_cache, expected_rack, expected_board, expected_device):
    """Helper to validate the info cache."""

    assert isinstance(info_cache, dict)
    assert expected_rack in info_cache

    rack = info_cache[expected_rack]
    assert 'rack' in rack
    assert 'boards' in rack
    assert rack['rack'] == expected_rack
    assert isinstance(rack['boards'], dict)
    assert expected_board in rack['boards']

    board = rack['boards'][expected_board]
    assert 'board' in board
    assert 'devices' in board
    assert board['board'] == expected_board
    assert isinstance(board['devices'], dict)
    assert expected_device in board['devices']

    device = board['devices'][expected_device]
    expected_keys = [
        'timestamp', 'uid', 'kind', 'metadata', 'plugin', 'info', 'location', 'output'
    ]
    for k in expected_keys:
        assert k in device
