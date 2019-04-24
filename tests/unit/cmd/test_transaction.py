
import asynctest
import pytest
from synse_grpc import api
from synse_grpc.errors import PluginError

from synse_server import errors
from synse_server.cmd import transaction


@pytest.mark.asyncio
async def test_transaction_not_found():
    with asynctest.patch('synse_server.cache.get_transaction') as mock_get:
        mock_get.return_value = None

        with pytest.raises(errors.NotFound):
            await transaction.transaction('123')

    mock_get.assert_called_once()
    mock_get.assert_called_with('123')


@pytest.mark.asyncio
async def test_transaction_no_plugin_id():
    with asynctest.patch('synse_server.cache.get_transaction') as mock_get:
        mock_get.return_value = {
            'device': 'test-device',
        }

        with pytest.raises(errors.ServerError):
            await transaction.transaction('123')

    mock_get.assert_called_once()
    mock_get.assert_called_with('123')


@pytest.mark.asyncio
async def test_transaction_plugin_not_found():
    with asynctest.patch('synse_server.cache.get_transaction') as mock_get:
        with asynctest.patch('synse_server.plugin.PluginManager.get') as mock_plugin_get:
            mock_plugin_get.return_value = None

            mock_get.return_value = {
                'plugin': 'test-plugin',
                'device': 'test-device',
            }

            with pytest.raises(errors.NotFound):
                await transaction.transaction('123')

    mock_get.assert_called_once()
    mock_get.assert_called_with('123')
    mock_plugin_get.assert_called_once()
    mock_plugin_get.assert_called_with('test-plugin')


@pytest.mark.asyncio
async def test_transaction_client_unexpected_error(mocker, simple_plugin):
    # Mock test data
    mock_txn = mocker.patch(
        'synse_grpc.client.PluginClientV3.transaction',
        side_effect=ValueError(),
    )

    # --- Test case -----------------------------
    with asynctest.patch('synse_server.cache.get_transaction') as mock_get:
        with asynctest.patch('synse_server.plugin.PluginManager.get') as mock_plugin_get:
            mock_plugin_get.return_value = simple_plugin
            simple_plugin.active = True

            mock_get.return_value = {
                'plugin': 'test-plugin',
                'device': 'test-device',
            }

            with pytest.raises(errors.ServerError):
                await transaction.transaction('123')

            # Verify the plugin was marked inactive due to the unexpected exception.
            assert simple_plugin.active is False

    mock_get.assert_called_once()
    mock_get.assert_called_with('123')
    mock_plugin_get.assert_called_once()
    mock_plugin_get.assert_called_with('test-plugin')
    mock_txn.assert_called_once()
    mock_txn.assert_called_with('123')


@pytest.mark.asyncio
async def test_transaction_client_expected_error(mocker, simple_plugin):
    # Mock test data
    mock_txn = mocker.patch(
        'synse_grpc.client.PluginClientV3.transaction',
        side_effect=PluginError(),
    )

    # --- Test case -----------------------------
    with asynctest.patch('synse_server.cache.get_transaction') as mock_get:
        with asynctest.patch('synse_server.plugin.PluginManager.get') as mock_plugin_get:
            mock_plugin_get.return_value = simple_plugin
            simple_plugin.active = True

            mock_get.return_value = {
                'plugin': 'test-plugin',
                'device': 'test-device',
            }

            with pytest.raises(errors.ServerError):
                await transaction.transaction('123')

            # Verify the plugin was not marked inactive, as the exception was expected.
            assert simple_plugin.active is True

    mock_get.assert_called_once()
    mock_get.assert_called_with('123')
    mock_plugin_get.assert_called_once()
    mock_plugin_get.assert_called_with('test-plugin')
    mock_txn.assert_called_once()
    mock_txn.assert_called_with('123')


@pytest.mark.asyncio
async def test_transaction_client_ok(mocker, simple_plugin):
    # Mock test data
    mock_txn = mocker.patch(
        'synse_grpc.client.PluginClientV3.transaction',
        return_value=api.V3TransactionStatus(
            id='123',
            created='2019-04-22T13:30:00Z',
            updated='2019-04-22T13:31:00Z',
            status=api.DONE,
            context=api.V3WriteData(
                action='test',
            ),
        ),
    )

    # --- Test case -----------------------------
    with asynctest.patch('synse_server.cache.get_transaction') as mock_get:
        with asynctest.patch('synse_server.plugin.PluginManager.get') as mock_plugin_get:
            mock_plugin_get.return_value = simple_plugin
            simple_plugin.active = True

            mock_get.return_value = {
                'plugin': 'test-plugin',
                'device': 'test-device',
            }

            resp = await transaction.transaction('123')
            assert resp == {
                'id': '123',
                'device': 'test-device',
                'created': '2019-04-22T13:30:00Z',
                'updated': '2019-04-22T13:31:00Z',
                'status': 'DONE',
                'message': '',
                'timeout': '',
                'context': {
                    'action': 'test',
                    'data': '',
                    'transaction': '',
                },
            }

            # Verify the plugin was not marked inactive, as there was no exception.
            assert simple_plugin.active is True

    mock_get.assert_called_once()
    mock_get.assert_called_with('123')
    mock_plugin_get.assert_called_once()
    mock_plugin_get.assert_called_with('test-plugin')
    mock_txn.assert_called_once()
    mock_txn.assert_called_with('123')


@pytest.mark.asyncio
async def test_transactions_none_cached(mocker):
    # Mock test data
    mock_get = mocker.patch(
        'synse_server.cache.get_cached_transaction_ids',
        return_value=[],
    )

    # --- Test case -----------------------------
    resp = await transaction.transactions()
    assert len(resp) == 0

    mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_transactions_one_cached(mocker):
    # Mock test data
    mock_get = mocker.patch(
        'synse_server.cache.get_cached_transaction_ids',
        return_value=[
            '123',
        ],
    )

    # --- Test case -----------------------------
    resp = await transaction.transactions()
    assert resp == ['123']

    mock_get.assert_called_once()


@pytest.mark.asyncio
async def test_transactions_multiple_cached(mocker):
    # Mock test data
    mock_get = mocker.patch(
        'synse_server.cache.get_cached_transaction_ids',
        return_value=[
            '123',
            '789',
            '456',
        ],
    )

    # --- Test case -----------------------------
    resp = await transaction.transactions()
    assert resp == ['123', '456', '789']

    mock_get.assert_called_once()
