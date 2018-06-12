"""Test the 'synse.proto.client' Synse Server module."""
# pylint: disable=redefined-outer-name,unused-argument

import grpc
import pytest
from synse_plugin import api as synse_api
from synse_plugin import grpc as synse_grpc

from synse import errors
from synse.proto import client

# --- Mock Methods ---


def mock_read(req, timeout):
    """Mock the internal read call."""
    return [
        synse_api.ReadResponse(
            timestamp='october',
            type='test',
            value='10'
        )
    ]


def mock_write(req, timeout):
    """Mock the internal write call."""
    return synse_api.Transactions(
        transactions={
            '12345': synse_api.WriteData(
                action='test',
                raw=[b'foo']
            )
        }
    )


def mock_metainfo(req, timeout):
    """Mock the internal metainfo call."""
    return [
        synse_api.MetainfoResponse(
            timestamp='october',
            uid='12345',
            type='thermistor',
            model='test',
            manufacturer='vapor io',
            protocol='foo',
            info='bar',
            location=synse_api.MetaLocation(
                rack='rack-1',
                board='vec'
            ),
            output=[
                synse_api.MetaOutput(
                    type='temperature',
                    data_type='float',
                    precision=3,
                    unit=synse_api.MetaOutputUnit(
                        name='celsius',
                        symbol='C'
                    ),
                    range=synse_api.MetaOutputRange(
                        min=0,
                        max=100
                    )
                )
            ]
        )
    ]


def mock_transaction(req, timeout):
    """Mock the internal transaction call."""
    return synse_api.WriteResponse(
        created='october',
        updated='november',
        status=3,
        state=0,
    )

# --- Test Cases ---


def test_write_data():
    """Test initializing WriteData instances."""

    wd = client.WriteData()
    assert wd.action == ''
    assert wd.raw == []

    wd = client.WriteData(action='test')
    assert wd.action == 'test'
    assert wd.raw == []

    wd = client.WriteData(raw=[b'test'])
    assert wd.action == ''
    assert wd.raw == [b'test']

    wd = client.WriteData(action='test', raw=[b'test'])
    assert wd.action == 'test'
    assert wd.raw == [b'test']


def test_write_data_to_grpc():
    """Convert a WriteData instance to its gRPC equivalent."""

    wd = client.WriteData(action='test', raw=[b'test'])
    rpc = wd.to_grpc()

    assert isinstance(rpc, synse_api.WriteData)
    assert rpc.action == 'test'
    assert rpc.raw == [b'test']


def test_get_client_exists():
    """Get a client when the client exists."""

    c = client.SynsePluginClient('test-cli', 'localhost:5000', 'tcp')
    assert len(client.SynsePluginClient._client_stubs) == 1

    test_cli = client.get_client('test-cli')
    assert test_cli == c
    assert len(client.SynsePluginClient._client_stubs) == 1


def test_get_client_does_not_exist():
    """Get a client when it does not already exist."""

    assert len(client.SynsePluginClient._client_stubs) == 0

    client.get_client('test-cli')

    assert len(client.SynsePluginClient._client_stubs) == 0


def test_client_init():
    """Verify the client initializes as expected."""

    c = client.SynsePluginClient('test-cli', 'test-cli.sock', 'unix')

    assert c.name == 'test-cli'
    assert c.addr == 'test-cli.sock'
    assert c.mode == 'unix'
    assert isinstance(c.channel, grpc.Channel)
    assert isinstance(c.stub, synse_grpc.InternalApiStub)


def test_client_init_bad_mode():
    """Verify the client fails to initialize when a bad mode is provided."""

    with pytest.raises(errors.InvalidArgumentsError):
        client.SynsePluginClient('test-cli', 'test-cli.sock', 'foo')


def test_client_read():
    """Test reading via the client."""

    c = client.SynsePluginClient('test', 'test.sock', 'unix')
    c.stub.Read = mock_read

    resp = c.read('rack-1', 'vec', '12345')

    assert isinstance(resp, list)
    assert len(resp) == 1
    assert isinstance(resp[0], synse_api.ReadResponse)


def test_client_write():
    """Test writing via the client."""

    c = client.SynsePluginClient('test', 'test.sock', 'unix')
    c.stub.Write = mock_write

    resp = c.write('rack-1', 'vec', '12345', [client.WriteData()])

    assert isinstance(resp, synse_api.Transactions)


def test_client_metainfo():
    """Test getting metainfo via the client."""

    c = client.SynsePluginClient('test', 'test.sock', 'unix')
    c.stub.Metainfo = mock_metainfo

    resp = c.metainfo()

    assert isinstance(resp, list)
    assert len(resp) == 1
    assert isinstance(resp[0], synse_api.MetainfoResponse)


def test_client_transaction():
    """Test checking a transaction via the client."""

    c = client.SynsePluginClient('test', 'test.sock', 'unix')
    c.stub.TransactionCheck = mock_transaction

    resp = c.check_transaction('abcdef')

    assert isinstance(resp, synse_api.WriteResponse)
