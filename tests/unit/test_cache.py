
import asynctest
import grpc
import pytest
from synse_grpc import api

from synse_server import cache


@pytest.mark.usefixtures('clear_txn_cache')
class TestTransactionCache:
    """Tests for the transaction cache."""

    @pytest.mark.asyncio
    async def test_get_transaction_ok(self, mocker):
        # Mock test data
        mocker.patch.dict('aiocache.SimpleMemoryCache._cache', {
            f'{cache.NS_TRANSACTION}txn-1': {
                'plugin': '123',
                'device': 'abc',
            },
        })

        # --- Test case -----------------------------
        txn = await cache.get_transaction('txn-1')
        assert txn == {
            'plugin': '123',
            'device': 'abc',
        }

    @pytest.mark.asyncio
    async def test_get_transaction_not_found(self, mocker):
        # Mock test data
        mocker.patch.dict('aiocache.SimpleMemoryCache._cache', {})

        # --- Test case -----------------------------
        txn = await cache.get_transaction('txn-1')
        assert txn is None

    @pytest.mark.asyncio
    async def test_get_transaction_needs_ns(self, mocker):
        # Mock test data
        mocker.patch.dict('aiocache.SimpleMemoryCache._cache', {
            'txn-1': {  # no txn namespace attached to key
                'plugin': '123',
                'device': 'abc',
            },
        })

        # --- Test case -----------------------------
        txn = await cache.get_transaction('txn-1')
        assert txn is None

    def test_get_cached_transaction_ids_empty(self, mocker):
        # Mock test data
        mocker.patch.dict('aiocache.SimpleMemoryCache._cache', {})

        # --- Test case -----------------------------
        txn_ids = cache.get_cached_transaction_ids()
        assert len(txn_ids) == 0

    def test_get_cached_transaction_ids_one(self, mocker):
        # Mock test data
        mocker.patch.dict('aiocache.SimpleMemoryCache._cache', {
            f'{cache.NS_TRANSACTION}txn-1': {
                'plugin': '123',
                'device': 'abc',
            },
        })

        # --- Test case -----------------------------
        txn_ids = cache.get_cached_transaction_ids()
        assert len(txn_ids) == 1
        assert 'txn-1' in txn_ids

    def test_get_cached_transaction_ids_multiple(self, mocker):
        # Mock test data
        mocker.patch.dict('aiocache.SimpleMemoryCache._cache', {
            f'{cache.NS_TRANSACTION}txn-1': {
                'plugin': '123',
                'device': 'abc',
            },
            f'{cache.NS_TRANSACTION}txn-2': {
                'plugin': '123',
                'device': 'def',
            },
            f'{cache.NS_TRANSACTION}txn-3': {
                'plugin': '123',
                'device': 'ghi',
            },
            f'{cache.NS_DEVICE}dev-1': {
                'device': '1',
            },
            f'{cache.NS_DEVICE}dev-2': {
                'device': '2',
            },
            f'{cache.NS_DEVICE}dev-3': {
                'device': '3',
            },
        })

        # --- Test case -----------------------------
        txn_ids = cache.get_cached_transaction_ids()
        assert len(txn_ids) == 3
        assert 'txn-1' in txn_ids
        assert 'txn-2' in txn_ids
        assert 'txn-3' in txn_ids

    @pytest.mark.asyncio
    async def test_add_transaction_new_transaction(self):
        assert len(cache.transaction_cache._cache) == 0

        await cache.add_transaction('txn-1', 'abc', '123')

        assert len(cache.transaction_cache._cache) == 1
        assert f'{cache.NS_TRANSACTION}txn-1' in cache.transaction_cache._cache

    @pytest.mark.asyncio
    async def test_add_transaction_existing_id(self, mocker):
        # Mock test data
        mocker.patch.dict('aiocache.SimpleMemoryCache._cache', {
            f'{cache.NS_TRANSACTION}txn-1': {
                'plugin': '123',
                'device': 'abc',
            },
        })

        # --- Test case -----------------------------
        assert len(cache.transaction_cache._cache) == 1

        await cache.add_transaction('txn-1', 'def', '456')

        assert len(cache.transaction_cache._cache) == 1
        assert f'{cache.NS_TRANSACTION}txn-1' in cache.transaction_cache._cache
        assert cache.transaction_cache._cache[f'{cache.NS_TRANSACTION}txn-1'] == {
            'plugin': '456',
            'device': 'def',
        }


@pytest.mark.usefixtures('clear_device_cache')
class TestDeviceCache:
    """Tests for the device cache."""

    @pytest.mark.asyncio
    async def test_update_device_cache_no_plugins(self, mocker):
        # Mock test data
        mocker.patch.dict('synse_server.plugin.PluginManager.plugins', {})

        mock_devices = mocker.patch(
            'synse_grpc.client.PluginClientV3.devices',
            return_value=[],
        )

        # --- Test case -----------------------------
        assert len(cache.device_cache._cache) == 0

        await cache.update_device_cache()

        assert len(cache.device_cache._cache) == 0

        mock_devices.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_device_cache_no_devices(self, mocker, simple_plugin):
        # Mock test data
        mocker.patch.dict('synse_server.plugin.PluginManager.plugins', {
            '123': simple_plugin,
            '456': simple_plugin,
        })

        mock_devices = mocker.patch(
            'synse_grpc.client.PluginClientV3.devices',
            return_value=[],
        )

        # --- Test case -----------------------------
        assert len(cache.device_cache._cache) == 0

        await cache.update_device_cache()

        assert len(cache.device_cache._cache) == 0

        mock_devices.assert_called()
        mock_devices.assert_has_calls([
            mocker.call(),
            mocker.call(),
        ])

    @pytest.mark.asyncio
    async def test_update_device_cache_devices_rpc_error(self, mocker, simple_plugin):
        # Mock test data
        mocker.patch.dict('synse_server.plugin.PluginManager.plugins', {
            '123': simple_plugin,
            '456': simple_plugin,
        })

        mock_devices = mocker.patch(
            'synse_grpc.client.PluginClientV3.devices',
            side_effect=grpc.RpcError(),
        )

        # --- Test case -----------------------------
        assert len(cache.device_cache._cache) == 0

        await cache.update_device_cache()

        assert len(cache.device_cache._cache) == 0

        mock_devices.assert_called()
        mock_devices.assert_has_calls([
            mocker.call(),
            mocker.call(),
        ])

    @pytest.mark.asyncio
    async def test_update_device_cache_devices_error(self, mocker, simple_plugin):
        # Mock test data
        mocker.patch.dict('synse_server.plugin.PluginManager.plugins', {
            '123': simple_plugin,
            '456': simple_plugin,
        })

        mock_devices = mocker.patch(
            'synse_grpc.client.PluginClientV3.devices',
            side_effect=ValueError(),
        )

        # --- Test case -----------------------------
        assert len(cache.device_cache._cache) == 0

        with pytest.raises(ValueError):
            await cache.update_device_cache()

        assert len(cache.device_cache._cache) == 0

        mock_devices.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_device_cache_ok(self, mocker, simple_plugin):
        # Mock test data
        mocker.patch.dict('synse_server.plugin.PluginManager.plugins', {
            '123': simple_plugin,
            '456': simple_plugin,
        })

        mock_devices = mocker.patch(
            'synse_grpc.client.PluginClientV3.devices',
            return_value=[
                api.V3Device(
                    tags=[
                        api.V3Tag(namespace='system', annotation='id', label='1'),
                        api.V3Tag(namespace='system', annotation='type', label='temperature'),
                        api.V3Tag(label='foo'),
                        api.V3Tag(namespace='default', label='foo'),
                        api.V3Tag(namespace='default', label='foo'),
                        api.V3Tag(namespace='vapor', label='bar'),
                        api.V3Tag(annotation='unit', label='test'),
                    ],
                ),
                api.V3Device(
                    tags=[
                        api.V3Tag(namespace='system', annotation='id', label='2'),
                        api.V3Tag(namespace='system', annotation='type', label='temperature'),
                        api.V3Tag(label='foo'),
                        api.V3Tag(namespace='default', label='bar'),
                        api.V3Tag(namespace='default', label='foo'),
                    ],
                ),
                api.V3Device(
                    tags=[
                        api.V3Tag(namespace='system', annotation='id', label='3'),
                        api.V3Tag(namespace='system', annotation='type', label='humidity'),
                        api.V3Tag(label='bar'),
                        api.V3Tag(namespace='vapor', label='bar'),
                        api.V3Tag(namespace='vapor', label='test'),
                        api.V3Tag(annotation='unit', label='test'),
                        api.V3Tag(annotation='integration', label='test'),
                    ],
                ),
            ],
        )

        # --- Test case -----------------------------
        assert len(cache.device_cache._cache) == 0

        await cache.update_device_cache()

        assert len(cache.device_cache._cache) == 13
        assert f'{cache.NS_DEVICE}system/id:1' in cache.device_cache._cache
        assert f'{cache.NS_DEVICE}system/id:2' in cache.device_cache._cache
        assert f'{cache.NS_DEVICE}system/id:3' in cache.device_cache._cache
        assert f'{cache.NS_DEVICE}system/type:temperature' in cache.device_cache._cache
        assert f'{cache.NS_DEVICE}system/type:humidity' in cache.device_cache._cache
        assert f'{cache.NS_DEVICE}foo' in cache.device_cache._cache
        assert f'{cache.NS_DEVICE}bar' in cache.device_cache._cache
        assert f'{cache.NS_DEVICE}default/foo' in cache.device_cache._cache
        assert f'{cache.NS_DEVICE}default/bar' in cache.device_cache._cache
        assert f'{cache.NS_DEVICE}vapor/bar' in cache.device_cache._cache
        assert f'{cache.NS_DEVICE}vapor/test' in cache.device_cache._cache
        assert f'{cache.NS_DEVICE}unit:test' in cache.device_cache._cache
        assert f'{cache.NS_DEVICE}integration:test' in cache.device_cache._cache

        mock_devices.assert_called()
        mock_devices.assert_has_calls([
            mocker.call(),
            mocker.call(),
        ])

    @pytest.mark.asyncio
    async def test_get_device_ok(self, mocker, simple_device):
        # Mock test data
        mocker.patch.dict('aiocache.SimpleMemoryCache._cache', {
            f'{cache.NS_DEVICE}system/id:{simple_device.id}': [simple_device],
        })

        # --- Test case -----------------------------
        device = await cache.get_device('test-device-1')
        assert device == simple_device

    @pytest.mark.asyncio
    async def test_get_device_not_found(self, mocker):
        # Mock test data
        mocker.patch.dict('aiocache.SimpleMemoryCache._cache', {})

        # --- Test case -----------------------------
        device = await cache.get_device('test-device-1')
        assert device is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'tags', [
            [],
            ['foo'],
            ['default/foo'],
            ['vapor:foo'],
            ['default/vapor:foo'],
            ['foo', 'bar', 'baz'],
            ['default/foo', 'system/bar', 'baz'],
            ['default/foo', 'something:bar', 'baz'],
        ]
    )
    async def test_get_devices_no_devices(self, mocker, tags):
        # Mock test data
        mocker.patch.dict('aiocache.SimpleMemoryCache._cache', {})

        # --- Test case -----------------------------
        devices = await cache.get_devices(*tags)
        assert len(devices) == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'tags,expected', [
            ([], 3),
            (['system/id:dev-1'], 1),
            (['system/id:dev-2'], 1),
            (['system/id:dev-3'], 1),
            (['system/id:dev-3', 'system/id:dev-1'], 0),
            (['system/type:temperature'], 2),
            (['system/type:humidity'], 1),
            (['system/type:led'], 0),
            (['foo', 'vapor/baz'], 1),
            (['foo', 'vapor/type:fun'], 0),
            (['system/type:temperature', 'vapor/type:fun'], 1),
            (['vapor/baz', 'vapor/type:fun'], 1),
        ]
    )
    async def test_get_devices_ok(self, mocker, tags, expected):
        dev1 = api.V3Device(id='dev-1')
        dev2 = api.V3Device(id='dev-2')
        dev3 = api.V3Device(id='dev-3')

        # Mock test data
        mocker.patch.dict('aiocache.SimpleMemoryCache._cache', {
            f'{cache.NS_DEVICE}system/id:{dev1.id}': [dev1],
            f'{cache.NS_DEVICE}system/id:{dev2.id}': [dev2],
            f'{cache.NS_DEVICE}system/id:{dev3.id}': [dev3],
            f'{cache.NS_DEVICE}system/type:temperature': [dev1, dev2],
            f'{cache.NS_DEVICE}system/type:humidity': [dev3],
            f'{cache.NS_DEVICE}foo': [dev1],
            f'{cache.NS_DEVICE}default/bar': [dev2],
            f'{cache.NS_DEVICE}default/baz': [dev3],
            f'{cache.NS_DEVICE}vapor/baz': [dev1, dev3],
            f'{cache.NS_DEVICE}vapor/type:fun': [dev2, dev3],
        })

        # --- Test case -----------------------------
        devices = await cache.get_devices(*tags)
        assert len(devices) == expected

    def test_get_cached_device_tags_no_tags(self, mocker):
        # Mock test data
        mocker.patch.dict('aiocache.SimpleMemoryCache._cache', {})

        # --- Test case -----------------------------
        tags = cache.get_cached_device_tags()
        assert len(tags) == 0

    def test_get_cached_device_tags_one_tag(self, mocker, simple_device):
        # Mock test data
        mocker.patch.dict('aiocache.SimpleMemoryCache._cache', {
            f'{cache.NS_DEVICE}foo': [simple_device],
        })

        # --- Test case -----------------------------
        tags = cache.get_cached_device_tags()
        assert len(tags) == 1
        assert 'foo' in tags

    def test_get_cached_device_tags_multiple_tags(self, mocker, simple_device):
        # Mock test data
        mocker.patch.dict('aiocache.SimpleMemoryCache._cache', {
            f'{cache.NS_DEVICE}foo': [simple_device],
            f'{cache.NS_DEVICE}vapor/baz': [simple_device, simple_device],
            f'{cache.NS_DEVICE}vapor/type:fun': [simple_device, simple_device],
        })

        # --- Test case -----------------------------
        tags = cache.get_cached_device_tags()
        assert len(tags) == 3
        assert 'foo' in tags
        assert 'vapor/baz' in tags
        assert 'vapor/type:fun' in tags

    @pytest.mark.asyncio
    async def test_get_plugin_no_device(self):
        with asynctest.patch('synse_server.cache.get_device') as mock_get:
            mock_get.return_value = None

            plugin = await cache.get_plugin('device-1')
            assert plugin is None

        mock_get.assert_called_once()
        mock_get.assert_called_with('device-1')

    @pytest.mark.asyncio
    async def test_get_plugin_no_plugin(self, simple_device):
        with asynctest.patch('synse_server.cache.get_device') as mock_get:
            mock_get.return_value = simple_device

            plugin = await cache.get_plugin('device-1')
            assert plugin is None

        mock_get.assert_called_once()
        mock_get.assert_called_with('device-1')

    @pytest.mark.asyncio
    async def test_get_plugin_ok(self, mocker, simple_plugin, simple_device):
        # Mock test data
        mocker.patch.dict('synse_server.plugin.PluginManager.plugins', {
            '123': simple_plugin,
        })

        # --- Test case -----------------------------
        with asynctest.patch('synse_server.cache.get_device') as mock_get:
            mock_get.return_value = simple_device

            plugin = await cache.get_plugin('device-1')
            assert plugin == simple_plugin

        mock_get.assert_called_once()
        mock_get.assert_called_with('device-1')
