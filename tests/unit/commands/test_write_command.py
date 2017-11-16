"""Test the 'synse.commands.write' Synse Server module."""
# pylint: disable=redefined-outer-name,unused-argument,line-too-long

import os
import shutil

import asynctest
import pytest
from synse_plugin import api

import synse.cache
from synse import errors, plugin
from synse.commands.write import write
from synse.proto.client import SynseInternalClient
from synse.scheme.write import WriteResponse


@pytest.fixture(scope='module')
def setup():
    """Fixture to setup/teardown the module tests."""

    # create a temp directory for test data
    if not os.path.isdir('tmp'):
        os.makedirs('tmp')

    # create a dummy file as test data
    open('tmp/foo', 'w').close()

    yield

    if os.path.isdir('tmp'):
        shutil.rmtree('tmp')


def mockgetdevicemeta(rack, board, device):
    """Mock method to monkeypatch the get_device_meta method."""
    return api.MetainfoResponse(
        timestamp='october',
        uid='12345',
        type='thermistor',
        model='test',
        manufacturer='vapor io',
        protocol='foo',  # this will be the name of the plugin we look up
        info='bar',
        location=api.MetaLocation(
            rack='rack-1',
            board='vec'
        ),
        output=[
            api.MetaOutput(
                type='temperature',
                data_type='float',
                precision=3,
                unit=api.MetaOutputUnit(
                    name='celsius',
                    symbol='C'
                ),
                range=api.MetaOutputRange(
                    min=0,
                    max=100
                )
            )
        ]
    )


def mocktransactionadd(tid, ctx, name):
    """Fixture to mock a failure when adding transaction to cache."""
    return False


def mockwrite(self, rack, board, device, data):
    """Mock method to monkeypatch the client write method."""
    return api.Transactions(
        transactions={
            'abcdef': api.WriteData(
                action=data[0].action,
                raw=data[0].raw
            )
        }
    )


@pytest.fixture()
def mock_get_device_meta(monkeypatch):
    """Fixture to monkeypatch the cache device meta lookup."""
    mock = asynctest.CoroutineMock(synse.cache.get_device_meta, side_effect=mockgetdevicemeta)
    monkeypatch.setattr(synse.cache, 'get_device_meta', mock)
    return mock_get_device_meta


@pytest.fixture()
def mock_transaction_add(monkeypatch):
    """Fixture to monkeypatch the cache transaction add."""
    mock = asynctest.CoroutineMock(synse.cache.add_transaction, side_effect=mocktransactionadd)
    monkeypatch.setattr(synse.cache, 'add_transaction', mock)
    return mock_transaction_add


@pytest.fixture()
def mock_client_write(monkeypatch):
    """Fixture to monkeypatch the grpc client's write method."""
    monkeypatch.setattr(SynseInternalClient, 'write', mockwrite)
    return mock_client_write


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
async def test_write_command_no_device():
    """Get a WriteResponse when the device doesn't exist."""

    # FIXME - it would be nice to use pytest.raises, but it seems like it isn't
    # properly trapping the exception for further testing.
    try:
        data = {'action': 'foo', 'raw': 'bar'}
        await write('rack-1', 'vec', '12345', data)
    except errors.SynseError as e:
        assert e.error_id == errors.DEVICE_NOT_FOUND


@pytest.mark.asyncio
async def test_write_command_no_plugin(mock_get_device_meta):
    """Get a WriteResponse when the plugin doesn't exist."""

    # FIXME - it would be nice to use pytest.raises, but it seems like it isn't
    # properly trapping the exception for further testing.
    try:
        data = {'action': 'foo', 'raw': 'bar'}
        await write('rack-1', 'vec', '12345', data)
    except errors.SynseError as e:
        assert e.error_id == errors.PLUGIN_NOT_FOUND


@pytest.mark.asyncio
async def test_write_command_grpc_err(mock_get_device_meta, make_plugin):
    """Get a WriteResponse when the plugin exists but cant communicate with it."""

    # FIXME - it would be nice to use pytest.raises, but it seems like it isn't
    # properly trapping the exception for further testing.
    try:
        data = {'action': 'foo', 'raw': 'bar'}
        await write('rack-1', 'vec', '12345', data)
    except errors.SynseError as e:
        assert e.error_id == errors.FAILED_WRITE_COMMAND


@pytest.mark.asyncio
async def test_write_command(mock_get_device_meta, mock_client_write, make_plugin):
    """Get a WriteResponse when the plugin exists."""

    data = {'action': 'foo', 'raw': 'bar'}
    resp = await write('rack-1', 'vec', '12345', data)

    assert isinstance(resp, WriteResponse)
    assert resp.data == [
        {
            'context': {
                'action': 'foo',
                'raw': [b'bar']
            },
            'transaction': 'abcdef'
        }
    ]


@pytest.mark.asyncio
async def test_write_command_failed_add(mock_get_device_meta, mock_transaction_add, mock_client_write, make_plugin):
    """Get a WriteResponse when the plugin exists but the transaction isn't added."""

    data = {'action': 'foo', 'raw': 'bar'}

    # in this case, nothing happens other than a message being logged
    # out -- should more be done?
    resp = await write('rack-1', 'vec', '12345', data)

    assert isinstance(resp, WriteResponse)
    assert resp.data == [
        {
            'context': {
                'action': 'foo',
                'raw': [b'bar']
            },
            'transaction': 'abcdef'
        }
    ]
