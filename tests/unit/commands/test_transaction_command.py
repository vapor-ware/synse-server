"""Test the 'synse_server.commands.transaction' Synse Server module."""
# pylint: disable=redefined-outer-name,unused-argument,line-too-long


import asynctest
import grpc
import pytest
from synse_grpc import api

import synse_server.cache
from synse_server import errors, plugin
from synse_server.commands.transaction import check_transaction
from synse_server.proto.client import PluginClient, PluginTCPClient
from synse_server.scheme.transaction import (TransactionListResponse,
                                      TransactionResponse)


def mockgettransaction(transaction):
    """Mock method to monkeypatch the get_transaction method."""
    # here, we hijack the 'transaction' input and make it the name of the plugin.
    # this allows us to use different plugin names when we are testing.
    return {
        'plugin': transaction,
        'context': {
            'action': 'foo',
            'data': b'bar'
        }
    }


def mockchecktransaction(self, transaction_id):
    """Mock method to monkeypatch the client check_transaction method."""
    return [api.WriteResponse(
        created='october',
        updated='november',
        status=3,
        state=0,
    )]


def mockchecktransactionfail(self, transaction_id):
    """Mock method to monkeypatch the client check_transaction method to fail."""
    raise grpc.RpcError()


@pytest.fixture()
def mock_get_transaction(monkeypatch):
    """Fixture to monkeypatch the cache transaction lookup."""
    mock = asynctest.CoroutineMock(synse_server.cache.get_transaction, side_effect=mockgettransaction)
    monkeypatch.setattr(synse_server.cache, 'get_transaction', mock)
    return mock_get_transaction


@pytest.fixture()
def mock_client_transaction(monkeypatch):
    """Fixture to monkeypatch the grpc client's transaction method."""
    monkeypatch.setattr(PluginClient, 'transaction', mockchecktransaction)
    return mock_client_transaction


@pytest.fixture()
def mock_client_transaction_fail(monkeypatch):
    """Fixture to monkeypatch the grpc client's transaction method to fail."""
    monkeypatch.setattr(PluginClient, 'transaction', mockchecktransactionfail)
    return mock_client_transaction_fail


@pytest.fixture()
def make_plugin():
    """Fixture to create and register a plugin for testing."""

    plugin_id = 'vaporio/foo+tcp@localhost:9999'

    # make a dummy plugin for the tests to use
    if plugin_id not in plugin.Plugin.manager.plugins:
        plugin.Plugin(
            metadata=api.Metadata(
                name='foo',
                tag='vaporio/foo'
            ),
            address='localhost:9999',
            plugin_client=PluginTCPClient('localhost:9999')
        )

    yield

    if plugin_id in plugin.Plugin.manager.plugins:
        del plugin.Plugin.manager.plugins[plugin_id]


@pytest.mark.asyncio
async def test_transaction_command_no_plugin_name(mock_get_transaction):
    """Get a TransactionResponse when the plugin name doesn't exist."""

    # FIXME - it would be nice to use pytest.raises, but it seems like it isn't
    # properly trapping the exception for further testing.
    try:
        await check_transaction(None)
    except errors.SynseError as e:
        assert e.error_id == errors.TRANSACTION_NOT_FOUND


@pytest.mark.asyncio
async def test_transaction_command_no_plugin(mock_get_transaction):
    """Get a TransactionResponse when the plugin doesn't exist."""

    # FIXME - it would be nice to use pytest.raises, but it seems like it isn't
    # properly trapping the exception for further testing.
    try:
        await check_transaction('bar')
    except errors.SynseError as e:
        assert e.error_id == errors.PLUGIN_NOT_FOUND


@pytest.mark.asyncio
async def test_transaction_command_grpc_err(mock_get_transaction, mock_client_transaction_fail, make_plugin):
    """Get a TransactionResponse when the plugin exists but cant communicate with it."""

    # FIXME - it would be nice to use pytest.raises, but it seems like it isn't
    # properly trapping the exception for further testing.
    try:
        await check_transaction('vaporio/foo+tcp@localhost:9999')
    except errors.SynseError as e:
        assert e.error_id == errors.FAILED_TRANSACTION_COMMAND


@pytest.mark.asyncio
async def test_transaction_command_no_transaction(clear_caches):
    """Get a transaction that doesn't exist in the cache."""

    # FIXME - it would be nice to use pytest.raises, but it seems like it isn't
    # properly trapping the exception for further testing.
    try:
        await check_transaction('nonexistent')
    except errors.SynseError as e:
        assert e.error_id == errors.TRANSACTION_NOT_FOUND


@pytest.mark.asyncio
async def test_transaction_command(mock_get_transaction, mock_client_transaction, make_plugin):
    """Get a TransactionResponse when the plugin exists."""

    resp = await check_transaction('vaporio/foo+tcp@localhost:9999')

    assert isinstance(resp, TransactionResponse)
    assert resp.data == {
        'id': 'vaporio/foo+tcp@localhost:9999',
        'context': {
            'action': 'foo',
            'data': b'bar'
        },
        'state': 'ok',
        'status': 'done',
        'created': 'october',
        'updated': 'november',
        'message': ''
    }


@pytest.mark.asyncio
async def test_transaction_none(clear_caches):
    """Pass None to the transaction command when no transactions exist."""

    resp = await check_transaction(None)
    assert isinstance(resp, TransactionListResponse)
    assert len(resp.data) == 0


@pytest.mark.asyncio
async def test_transaction_none2(clear_caches):
    """Pass None to the transaction command when transactions exist."""

    ok = await synse_server.cache.add_transaction('abc123', {'some': 'ctx'}, 'test-plugin')
    assert ok

    resp = await check_transaction(None)
    assert isinstance(resp, TransactionListResponse)
    assert len(resp.data) == 1
    assert 'abc123' in resp.data
