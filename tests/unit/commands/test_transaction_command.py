"""Test the 'synse.commands.transaction' Synse Server module.
"""

import os
import shutil

import asynctest
import pytest
from synse_plugin import api

from synse import errors, plugin
import synse.cache
from synse.proto.client import SynseInternalClient
from synse.commands.transaction import check_transaction
from synse.scheme.transaction import TransactionResponse


@pytest.fixture(scope='module')
def setup():
    """Fixture to setup/teardown the module tests"""

    # create a temp directory for test data
    if not os.path.isdir('tmp'):
        os.makedirs('tmp')

    # create a dummy file as test data
    open('tmp/foo', 'w').close()

    yield

    if os.path.isdir('tmp'):
        shutil.rmtree('tmp')


def mockgettransaction(transaction):
    """Mock method to monkeypatch the get_transaction method."""
    # here, we hijack the 'transaction' input and make it the name of the plugin.
    # this allows us to use different plugin names when we are testing.
    return {
        'plugin': transaction,
        'context': {
            'action': 'foo',
            'raw': [b'bar']
        }
    }


def mockchecktransaction(self, transaction_id):
    """Mock method to monkeypatch the client check_transaction method."""
    return api.WriteResponse(
        created='october',
        updated='november',
        status=3,
        state=0,
    )


@pytest.fixture()
def mock_get_transaction(monkeypatch):
    """Fixture to monkeypatch the cache transaction lookup."""
    mock = asynctest.CoroutineMock(synse.cache.get_transaction, side_effect=mockgettransaction)
    monkeypatch.setattr(synse.cache, 'get_transaction', mock)
    return mock_get_transaction


@pytest.fixture()
def mock_client_transaction(monkeypatch):
    """Fixture to monkeypatch the grpc client's transaction method."""
    monkeypatch.setattr(SynseInternalClient, 'check_transaction', mockchecktransaction)
    return mock_client_transaction


@pytest.fixture()
def make_plugin(setup):
    """Fixture to create and register a plugin for testing."""

    # make a dummy plugin for the tests to use
    if 'foo' not in plugin.Plugin.manager.plugins:
        plugin.Plugin('foo', 'tmp/foo')

    yield

    if 'foo' in plugin.Plugin.manager.plugins:
        del plugin.Plugin.manager.plugins['foo']


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
async def test_transaction_command_grpc_err(mock_get_transaction, make_plugin):
    """Get a TransactionResponse when the plugin exists but cant communicate with it."""

    # FIXME - it would be nice to use pytest.raises, but it seems like it isn't
    # properly trapping the exception for further testing.
    try:
        await check_transaction('foo')
    except errors.SynseError as e:
        assert e.error_id == errors.FAILED_TRANSACTION_COMMAND


@pytest.mark.asyncio
async def test_transaction_command(mock_get_transaction, mock_client_transaction, make_plugin):
    """Get a TransactionResponse when the plugin exists."""

    resp = await check_transaction('foo')

    assert isinstance(resp, TransactionResponse)
    assert resp.data == {
        'id': 'foo',
        'context': {
            'action': 'foo',
            'raw': [b'bar']
        },
        'state': 'ok',
        'status': 'done',
        'created': 'october',
        'updated': 'november',
        'message': ''
    }
