"""Test the 'synse.commands.read' Synse Server module."""
# pylint: disable=redefined-outer-name,unused-argument

import os
import shutil

import asynctest
import grpc
import pytest
from synse_plugin import api

import synse.cache
from synse import errors, plugin
from synse.commands.read import read
from synse.proto.client import SynseInternalClient
from synse.scheme.read import ReadResponse


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


def mockread(self, rack, board, device):
    """Mock method to monkeypatch the client read method."""
    return [api.ReadResponse(
        timestamp='october',
        type='temperature',
        value='10'
    )]


def mockreadfail(self, rack, board, device):
    """Mock method to monkeypatch the client read method to fail."""
    raise grpc.RpcError()


@pytest.fixture()
def mock_get_device_meta(monkeypatch):
    """Fixture to monkeypatch the cache device meta lookup."""
    mock = asynctest.CoroutineMock(synse.cache.get_device_meta, side_effect=mockgetdevicemeta)
    monkeypatch.setattr(synse.cache, 'get_device_meta', mock)
    return mock_get_device_meta


@pytest.fixture()
def mock_client_read(monkeypatch):
    """Fixture to monkeypatch the grpc client's read method."""
    monkeypatch.setattr(SynseInternalClient, 'read', mockread)
    return mock_client_read


@pytest.fixture()
def mock_client_read_fail(monkeypatch):
    """Fixture to monkeypatch the grpc client's read method to fail."""
    monkeypatch.setattr(SynseInternalClient, 'read', mockreadfail)
    return mock_client_read_fail


@pytest.fixture()
def make_plugin(setup):
    """Fixture to create and register a plugin for testing."""

    # make a dummy plugin for the tests to use
    if 'foo' not in plugin.Plugin.manager.plugins:
        plugin.Plugin('foo', 'tmp/foo', 'unix')

    yield

    if 'foo' in plugin.Plugin.manager.plugins:
        del plugin.Plugin.manager.plugins['foo']


@pytest.mark.asyncio
async def test_read_command_no_device(plugin_dir):
    """Get a ReadResponse when the device doesn't exist."""

    # FIXME - it would be nice to use pytest.raises, but it seems like it isn't
    # properly trapping the exception for further testing.
    try:
        await read('rack-1', 'vec', '12345')
    except errors.SynseError as e:
        assert e.error_id == errors.DEVICE_NOT_FOUND


@pytest.mark.asyncio
async def test_read_command_no_plugin(mock_get_device_meta):
    """Get a ReadResponse when the plugin doesn't exist."""

    # FIXME - it would be nice to use pytest.raises, but it seems like it isn't
    # properly trapping the exception for further testing.
    try:
        await read('rack-1', 'vec', '12345')
    except errors.SynseError as e:
        assert e.error_id == errors.PLUGIN_NOT_FOUND


@pytest.mark.asyncio
async def test_read_command_grpc_err(mock_get_device_meta, mock_client_read_fail, make_plugin):
    """Get a ReadResponse when the plugin exists but cant communicate with it."""

    # FIXME - it would be nice to use pytest.raises, but it seems like it isn't
    # properly trapping the exception for further testing.
    try:
        await read('rack-1', 'vec', '12345')
    except errors.SynseError as e:
        assert e.error_id == errors.FAILED_READ_COMMAND


@pytest.mark.asyncio
async def test_read_command(mock_get_device_meta, mock_client_read, make_plugin):
    """Get a ReadResponse when the plugin exists."""

    resp = await read('rack-1', 'vec', '12345')

    assert isinstance(resp, ReadResponse)
    assert resp.data == {
        'type': 'thermistor',
        'data': {
            'temperature': {
                'value': 10.0,
                'timestamp': 'october',
                'unit': {
                    'name': 'celsius',
                    'symbol': 'C'
                }
            }
        }
    }
