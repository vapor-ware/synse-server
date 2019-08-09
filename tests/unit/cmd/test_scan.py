
import asynctest
import pytest
from synse_grpc import api

from synse_server import cmd, errors


@pytest.mark.asyncio
async def test_scan_force_error():
    with asynctest.patch('synse_server.cache.update_device_cache') as mock_update:
        mock_update.side_effect = ValueError()

        with pytest.raises(errors.ServerError):
            await cmd.scan('default', [], '', force=True)

    mock_update.assert_called_once()


@pytest.mark.asyncio
async def test_scan_no_devices():
    with asynctest.patch('synse_server.cache.update_device_cache') as mock_update:
        with asynctest.patch('synse_server.cache.get_devices') as mock_get:
            mock_get.return_value = []

            resp = await cmd.scan('default', [['foo']], '', force=False)
            assert len(resp) == 0

    mock_update.assert_not_called()
    mock_get.assert_called_once()
    mock_get.assert_called_with('default/foo')


@pytest.mark.asyncio
async def test_scan_get_devices_errors():
    with asynctest.patch('synse_server.cache.update_device_cache') as mock_update:
        with asynctest.patch('synse_server.cache.get_devices') as mock_get:
            mock_get.side_effect = ValueError()

            with pytest.raises(errors.ServerError):
                await cmd.scan('default', [['foo', 'test/bar']], '', force=False)

    mock_update.assert_not_called()
    mock_get.assert_called_once()
    mock_get.assert_called_with('default/foo', 'test/bar')


@pytest.mark.asyncio
async def test_scan_invalid_keys():
    with asynctest.patch('synse_server.cache.update_device_cache') as mock_update:
        with asynctest.patch('synse_server.cache.get_devices') as mock_get:
            mock_get.return_value = [
                api.V3Device(
                    id='1',
                    type='foo',
                    plugin='abc',
                    tags=[
                        api.V3Tag(namespace='default', label='foo')
                    ]
                ),
                api.V3Device(
                    id='2',
                    type='foo',
                    plugin='def',
                    tags=[
                        api.V3Tag(namespace='default', label='foo')
                    ]
                ),
                api.V3Device(
                    id='3',
                    type='bar',
                    plugin='abc',
                    tags=[
                        api.V3Tag(namespace='default', label='foo')
                    ]
                ),
            ]

            with pytest.raises(errors.InvalidUsage):
                await cmd.scan('default', [['foo']], 'not-a-key,tags', force=False)

    mock_update.assert_not_called()
    mock_get.assert_called_once()
    mock_get.assert_called_with('default/foo')


@pytest.mark.asyncio
async def test_scan_ok():
    with asynctest.patch('synse_server.cache.update_device_cache') as mock_update:
        with asynctest.patch('synse_server.cache.get_devices') as mock_get:
            mock_get.return_value = [
                api.V3Device(
                    id='1',
                    type='foo',
                    plugin='abc',
                    tags=[
                        api.V3Tag(namespace='default', label='foo')
                    ]
                ),
                api.V3Device(
                    id='2',
                    type='foo',
                    plugin='def',
                    tags=[
                        api.V3Tag(namespace='default', label='foo')
                    ]
                ),
                api.V3Device(
                    id='3',
                    type='bar',
                    plugin='abc',
                    tags=[
                        api.V3Tag(namespace='default', label='foo')
                    ]
                ),
            ]

            resp = await cmd.scan('default', [['foo']], 'plugin,sortIndex,id', force=True)
            assert len(resp) == 3
            assert resp[0]['id'] == '1'
            assert resp[1]['id'] == '3'
            assert resp[2]['id'] == '2'

    mock_update.assert_called_once()
    mock_get.assert_called_once()
    mock_get.assert_called_with('default/foo')


@pytest.mark.asyncio
async def test_scan_sort_ok():
    with asynctest.patch('synse_server.cache.update_device_cache') as mock_update:
        with asynctest.patch('synse_server.cache.get_devices') as mock_get:
            mock_get.return_value = [
                api.V3Device(
                    id='1',
                    type='foo',
                    plugin='abc',
                    tags=[
                        api.V3Tag(namespace='default', label='foo')
                    ]
                ),
                api.V3Device(
                    id='2',
                    type='foo',
                    plugin='def',
                    tags=[
                        api.V3Tag(namespace='default', label='foo')
                    ]
                ),
                api.V3Device(
                    id='3',
                    type='bar',
                    plugin='abc',
                    tags=[
                        api.V3Tag(namespace='default', label='foo')
                    ]
                ),
            ]

            resp = await cmd.scan('default', [['foo']], 'type,plugin,id', force=True)
            assert len(resp) == 3
            assert resp[0]['id'] == '3'
            assert resp[1]['id'] == '1'
            assert resp[2]['id'] == '2'

    mock_update.assert_called_once()
    mock_get.assert_called_once()
    mock_get.assert_called_with('default/foo')
