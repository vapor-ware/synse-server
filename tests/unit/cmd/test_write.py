
import asynctest
import pytest
from synse_grpc import api

from synse_server import cmd, errors


@pytest.mark.asyncio
async def test_write_async_plugin_not_found(mocker):
    # Mock test data
    mock_write_async = mocker.patch(
        'synse_grpc.client.PluginClientV3.write_async',
    )

    # --- Test case -----------------------------
    with asynctest.patch('synse_server.cache.get_plugin') as mock_get:
        mock_get.return_value = None

        with pytest.raises(errors.NotFound):
            await cmd.write_async('123', {})

    mock_get.assert_called_once()
    mock_get.assert_called_with('123')
    mock_write_async.assert_not_called()


@pytest.mark.asyncio
async def test_write_async_get_plugin_error(mocker):
    # Mock test data
    mock_write_async = mocker.patch(
        'synse_grpc.client.PluginClientV3.write_async',
    )

    # --- Test case -----------------------------
    with asynctest.patch('synse_server.cache.get_plugin') as mock_get:
        mock_get.side_effect = ValueError()

        with pytest.raises(ValueError):
            await cmd.write_async('123', {})

    mock_get.assert_called_once()
    mock_get.assert_called_with('123')
    mock_write_async.assert_not_called()


@pytest.mark.asyncio
async def test_write_async_error(mocker, simple_plugin):
    # Mock test data
    mock_write_async = mocker.patch(
        'synse_grpc.client.PluginClientV3.write_async',
        side_effect=ValueError(),
    )

    # --- Test case -----------------------------
    with asynctest.patch('synse_server.cache.get_plugin') as mock_get:
        with asynctest.patch('synse_server.cache.add_transaction') as mock_add:
            mock_get.return_value = simple_plugin

            with pytest.raises(errors.ServerError):
                await cmd.write_async('123', {'action': 'foo'})

    mock_get.assert_called_once()
    mock_get.assert_called_with('123')
    mock_write_async.assert_called_once()
    mock_write_async.assert_called_with(device_id='123', data={'action': 'foo'})
    mock_add.assert_not_called()


@pytest.mark.asyncio
async def test_write_async_add_transaction_error(mocker, simple_plugin):
    # Mock test data
    mock_write_async = mocker.patch(
        'synse_grpc.client.PluginClientV3.write_async',
        return_value=[
            api.V3WriteTransaction(
                id='txn-1',
                device='abc',
                context=api.V3WriteData(
                    action='foo',
                ),
                timeout='5s',
            ),
        ],
    )

    # --- Test case -----------------------------
    with asynctest.patch('synse_server.cache.get_plugin') as mock_get:
        with asynctest.patch('synse_server.cache.add_transaction') as mock_add:
            mock_get.return_value = simple_plugin
            mock_add.side_effect = ValueError()

            with pytest.raises(errors.ServerError):
                await cmd.write_async('abc', {'action': 'foo'})

    mock_get.assert_called_once()
    mock_get.assert_called_with('abc')
    mock_write_async.assert_called_once()
    mock_write_async.assert_called_with(device_id='abc', data={'action': 'foo'})
    mock_add.assert_called_once()
    mock_add.assert_called_with('txn-1', 'abc', '123')


@pytest.mark.asyncio
async def test_write_async_ok(mocker, simple_plugin):
    # Mock test data
    mock_write_async = mocker.patch(
        'synse_grpc.client.PluginClientV3.write_async',
        return_value=[
            api.V3WriteTransaction(
                id='txn-1',
                device='abc',
                context=api.V3WriteData(
                    action='foo',
                ),
                timeout='5s',
            ),
            api.V3WriteTransaction(
                id='txn-2',
                device='abc',
                context=api.V3WriteData(
                    action='bar',
                ),
                timeout='5s',
            ),
            api.V3WriteTransaction(
                id='txn-3',
                device='abc',
                context=api.V3WriteData(
                    action='baz',
                ),
                timeout='5s',
            ),
        ],
    )

    # --- Test case -----------------------------
    with asynctest.patch('synse_server.cache.get_plugin') as mock_get:
        with asynctest.patch('synse_server.cache.add_transaction') as mock_add:
            mock_get.return_value = simple_plugin

            resp = await cmd.write_async(
                device_id='abc',
                payload=[
                    {'action': 'foo'},
                    {'action': 'bar'},
                    {'action': 'baz'},
                ],
            )
            assert resp == [
                {
                    'id': 'txn-1',
                    'device': 'abc',
                    'timeout': '5s',
                    'context': {
                        'action': 'foo',
                        'data': b'',
                        'transaction': '',
                    },
                },
                {
                    'id': 'txn-2',
                    'device': 'abc',
                    'timeout': '5s',
                    'context': {
                        'action': 'bar',
                        'data': b'',
                        'transaction': '',
                    },
                },
                {
                    'id': 'txn-3',
                    'device': 'abc',
                    'timeout': '5s',
                    'context': {
                        'action': 'baz',
                        'data': b'',
                        'transaction': '',
                    },
                },
            ]

    mock_get.assert_called_once()
    mock_get.assert_called_with('abc')
    mock_write_async.assert_called_once()
    mock_write_async.assert_called_with(
        device_id='abc',
        data=[
            {'action': 'foo'},
            {'action': 'bar'},
            {'action': 'baz'},
        ])
    mock_add.assert_called()
    mock_add.assert_has_calls([
        mocker.call('txn-1', 'abc', '123'),
        mocker.call('txn-2', 'abc', '123'),
        mocker.call('txn-3', 'abc', '123'),
    ])


@pytest.mark.asyncio
async def test_write_sync_plugin_not_found(mocker):
    # Mock test data
    mock_write_sync = mocker.patch(
        'synse_grpc.client.PluginClientV3.write_sync',
    )

    # --- Test case -----------------------------
    with asynctest.patch('synse_server.cache.get_plugin') as mock_get:
        mock_get.return_value = None

        with pytest.raises(errors.NotFound):
            await cmd.write_sync('123', {})

    mock_get.assert_called_once()
    mock_get.assert_called_with('123')
    mock_write_sync.assert_not_called()


@pytest.mark.asyncio
async def test_write_sync_get_plugin_error(mocker):
    # Mock test data
    mock_write_sync = mocker.patch(
        'synse_grpc.client.PluginClientV3.write_sync',
    )

    # --- Test case -----------------------------
    with asynctest.patch('synse_server.cache.get_plugin') as mock_get:
        mock_get.side_effect = ValueError()

        with pytest.raises(ValueError):
            await cmd.write_sync('123', {})

    mock_get.assert_called_once()
    mock_get.assert_called_with('123')
    mock_write_sync.assert_not_called()


@pytest.mark.asyncio
async def test_write_sync_error(mocker, simple_plugin):
    # Mock test data
    mock_write_sync = mocker.patch(
        'synse_grpc.client.PluginClientV3.write_sync',
        side_effect=ValueError(),
    )

    # --- Test case -----------------------------
    with asynctest.patch('synse_server.cache.get_plugin') as mock_get:
        with asynctest.patch('synse_server.cache.add_transaction') as mock_add:
            mock_get.return_value = simple_plugin

            with pytest.raises(errors.ServerError):
                await cmd.write_sync('123', {'action': 'foo'})

    mock_get.assert_called_once()
    mock_get.assert_called_with('123')
    mock_write_sync.assert_called_once()
    mock_write_sync.assert_called_with(device_id='123', data={'action': 'foo'})
    mock_add.assert_not_called()


@pytest.mark.asyncio
async def test_write_sync_add_transaction_error(mocker, simple_plugin):
    # Mock test data
    mock_write_sync = mocker.patch(
        'synse_grpc.client.PluginClientV3.write_sync',
        return_value=[
            api.V3TransactionStatus(
                id='txn-1',
                created='2019-04-22T13:30:00Z',
                updated='2019-04-22T13:31:00Z',
                status=api.DONE,
                context=api.V3WriteData(
                    action='foo',
                )
            ),
        ],
    )

    # --- Test case -----------------------------
    with asynctest.patch('synse_server.cache.get_plugin') as mock_get:
        with asynctest.patch('synse_server.cache.add_transaction') as mock_add:
            mock_get.return_value = simple_plugin
            mock_add.side_effect = ValueError()

            with pytest.raises(errors.ServerError):
                await cmd.write_sync('abc', {'action': 'foo'})

    mock_get.assert_called_once()
    mock_get.assert_called_with('abc')
    mock_write_sync.assert_called_once()
    mock_write_sync.assert_called_with(device_id='abc', data={'action': 'foo'})
    mock_add.assert_called_once()
    mock_add.assert_called_with('txn-1', 'abc', '123')


@pytest.mark.asyncio
async def test_write_sync_ok(mocker, simple_plugin):
    # Mock test data
    mock_write_sync = mocker.patch(
        'synse_grpc.client.PluginClientV3.write_sync',
        return_value=[
            api.V3TransactionStatus(
                id='txn-1',
                created='2019-04-22T13:30:00Z',
                updated='2019-04-22T13:31:00Z',
                status=api.DONE,
                context=api.V3WriteData(
                    action='foo',
                )
            ),
            api.V3TransactionStatus(
                id='txn-2',
                created='2019-04-22T13:30:00Z',
                updated='2019-04-22T13:31:00Z',
                status=api.DONE,
                context=api.V3WriteData(
                    action='bar',
                )
            ),
            api.V3TransactionStatus(
                id='txn-3',
                created='2019-04-22T13:30:00Z',
                updated='2019-04-22T13:31:00Z',
                status=api.DONE,
                context=api.V3WriteData(
                    action='baz',
                )
            ),
        ],
    )

    # --- Test case -----------------------------
    with asynctest.patch('synse_server.cache.get_plugin') as mock_get:
        with asynctest.patch('synse_server.cache.add_transaction') as mock_add:
            mock_get.return_value = simple_plugin

            resp = await cmd.write_sync(
                device_id='abc',
                payload=[
                    {'action': 'foo'},
                    {'action': 'bar'},
                    {'action': 'baz'},
                ],
            )
            assert resp == [
                {
                    'id': 'txn-1',
                    'device': 'abc',
                    'created': '2019-04-22T13:30:00Z',
                    'updated': '2019-04-22T13:31:00Z',
                    'message': '',
                    'timeout': '',
                    'status': 'DONE',
                    'context': {
                        'action': 'foo',
                        'data': b'',
                        'transaction': '',
                    },
                },
                {
                    'id': 'txn-2',
                    'device': 'abc',
                    'created': '2019-04-22T13:30:00Z',
                    'updated': '2019-04-22T13:31:00Z',
                    'message': '',
                    'timeout': '',
                    'status': 'DONE',
                    'context': {
                        'action': 'bar',
                        'data': b'',
                        'transaction': '',
                    },
                },
                {
                    'id': 'txn-3',
                    'device': 'abc',
                    'created': '2019-04-22T13:30:00Z',
                    'updated': '2019-04-22T13:31:00Z',
                    'message': '',
                    'timeout': '',
                    'status': 'DONE',
                    'context': {
                        'action': 'baz',
                        'data': b'',
                        'transaction': '',
                    },
                },
            ]

    mock_get.assert_called_once()
    mock_get.assert_called_with('abc')
    mock_write_sync.assert_called_once()
    mock_write_sync.assert_called_with(
        device_id='abc',
        data=[
            {'action': 'foo'},
            {'action': 'bar'},
            {'action': 'baz'},
        ])
    mock_add.assert_called()
    mock_add.assert_has_calls([
        mocker.call('txn-1', 'abc', '123'),
        mocker.call('txn-2', 'abc', '123'),
        mocker.call('txn-3', 'abc', '123'),
    ])
