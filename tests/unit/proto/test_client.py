"""Test the 'synse_server.proto.client' Synse Server module."""
# pylint: disable=redefined-outer-name,unused-argument

import os

import grpc
import pytest
import synse_grpc

from synse_server import config
from synse_server.proto import client

# --- Mock Methods ---


def mock_read(req, timeout):
    """Mock the internal read call."""
    return [
        synse_grpc.api.Reading(
            timestamp='october',
            type='test',
            int32_value=10
        )
    ]


def mock_read_cached(req, timeout):
    """Mock the internal read cached call."""
    return [
        synse_grpc.api.DeviceReading(
            rack='rack',
            board='board',
            device='device',
            reading=synse_grpc.api.Reading(
                timestamp='october',
                type='test',
                int32_value=10,
            )
        )
    ]


def mock_write(req, timeout):
    """Mock the internal write call."""
    return synse_grpc.api.Transactions(
        transactions={
            '12345': synse_grpc.api.WriteData(
                action='test',
                data=b'foo'
            )
        }
    )


def mock_device_info(req, timeout):
    """Mock the internal device info call."""
    return [
        synse_grpc.api.Device(
            timestamp='october',
            uid='12345',
            kind='thermistor',
            metadata=dict(
                model='test',
                manufacturer='vapor io',
            ),
            plugin='foo',
            info='bar',
            location=synse_grpc.api.Location(
                rack='rack-1',
                board='vec'
            ),
            output=[
                synse_grpc.api.Output(
                    type='temperature',
                    precision=3,
                    unit=synse_grpc.api.Unit(
                        name='celsius',
                        symbol='C'
                    )
                )
            ]
        )
    ]


def mock_transaction(req, timeout):
    """Mock the internal transaction call."""
    return [synse_grpc.api.WriteResponse(
        created='october',
        updated='november',
        status=3,
        state=0,
    )]


def mock_test(req, timeout):
    """Mock the internal grpc test call."""
    return synse_grpc.api.Status(ok=True)


def mock_health(req, timeout):
    """Mock the internal grpc health call."""
    return synse_grpc.api.PluginHealth(
        timestamp='now'
    )


def mock_metainfo(req, timeout):
    """Mock the internal grpc metainfo call."""
    return synse_grpc.api.Metadata(
        name='test'
    )


def mock_capabilities(req, timeout):
    """Mock the internal grpc capabilities call."""
    return [synse_grpc.api.DeviceCapability(
        kind='test',
        outputs=['foo', 'bar']
    )]


# --- Test Cases ---


def test_write_data():
    """Test initializing WriteData instances."""

    wd = client.WriteData()
    assert wd.action == ''
    assert wd.data == b''

    wd = client.WriteData(action='test')
    assert wd.action == 'test'
    assert wd.data == b''

    wd = client.WriteData(data=b'test')
    assert wd.action == ''
    assert wd.data == b'test'

    wd = client.WriteData(action='test', data=b'test')
    assert wd.action == 'test'
    assert wd.data == b'test'


def test_write_data_to_grpc():
    """Convert a WriteData instance to its gRPC equivalent."""

    wd = client.WriteData(action='test', data=b'test')
    rpc = wd.to_grpc()

    assert isinstance(rpc, synse_grpc.api.WriteData)
    assert rpc.action == 'test'
    assert rpc.data == b'test'


def test_init_base_client():
    """Initializing the base client should result in error."""

    with pytest.raises(NotImplementedError):
        _ = client.PluginClient(address='localhost')


def test_client_init():
    """Verify the client initializes as expected."""

    c = client.PluginUnixClient('foo/bar/test-cli.sock')

    assert c.address == 'foo/bar/test-cli.sock'
    assert c.type == 'unix'
    assert isinstance(c.channel, grpc.Channel)
    assert isinstance(c.grpc, synse_grpc.grpc.PluginStub)


def test_client_read():
    """Test reading via the client."""

    c = client.PluginUnixClient('foo/bar/test.sock')
    c.grpc.Read = mock_read

    resp = c.read('rack-1', 'vec', '12345')

    assert isinstance(resp, list)
    assert len(resp) == 1
    assert isinstance(resp[0], synse_grpc.api.Reading)


def test_client_read_cached():
    """Test reading plugin cache via the client."""

    c = client.PluginUnixClient('foo/bar/test.sock')
    c.grpc.ReadCached = mock_read_cached

    resp = [x for x in c.read_cached()]

    assert len(resp) == 1
    assert isinstance(resp[0], synse_grpc.api.DeviceReading)


def test_client_write():
    """Test writing via the client."""

    c = client.PluginUnixClient('foo/bar/test.sock')
    c.grpc.Write = mock_write

    resp = c.write('rack-1', 'vec', '12345', [client.WriteData()])

    assert isinstance(resp, synse_grpc.api.Transactions)


def test_client_devices():
    """Test getting device info via the client."""

    c = client.PluginUnixClient('foo/bar/test.sock')
    c.grpc.Devices = mock_device_info

    resp = c.devices()

    assert isinstance(resp, list)
    assert len(resp) == 1
    assert isinstance(resp[0], synse_grpc.api.Device)


def test_client_transaction():
    """Test checking a transaction via the client."""

    c = client.PluginUnixClient('foo/bar/test.sock')
    c.grpc.Transaction = mock_transaction

    resp = c.transaction('abcdef')

    assert isinstance(resp, list)
    assert isinstance(resp[0], synse_grpc.api.WriteResponse)


def test_client_test():
    """Test that a plugin is reachable."""

    c = client.PluginUnixClient('foo/bar/test.sock')
    c.grpc.Test = mock_test

    resp = c.test()

    assert isinstance(resp, synse_grpc.api.Status)


def test_client_health():
    """Test getting plugin health via the client."""

    c = client.PluginUnixClient('foo/bar/test.sock')
    c.grpc.Health = mock_health

    resp = c.health()

    assert isinstance(resp, synse_grpc.api.PluginHealth)


def test_client_metainfo():
    """Test getting plugin metainfo via the client."""

    c = client.PluginUnixClient('foo/bar/test.sock')
    c.grpc.Metainfo = mock_metainfo

    resp = c.metainfo()

    assert isinstance(resp, synse_grpc.api.Metadata)


def test_client_capabilities():
    """Test getting plugin capabilities via the client."""

    c = client.PluginUnixClient('foo/bar/test.sock')
    c.grpc.Capabilities = mock_capabilities

    resp = c.capabilities()

    assert isinstance(resp, list)
    assert len(resp) == 1
    assert isinstance(resp[0], synse_grpc.api.DeviceCapability)


def test_make_channel_insecure():
    """Test making the grpc channel for the plugin client.
    In this case, the channel will be insecure (no TLS configured).
    """

    c = client.PluginTCPClient('localhost')
    assert c.channel is not None
    assert c.channel._channel.target() == b'localhost'


def test_make_channel_secure():
    """Test making the grpc channel for the plugin client.
    In this case, the channel will be secure (TLS configured).
    """
    crt = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'test_data', 'test.crt')
    config.options.set('grpc.tls.cert', crt)

    c = client.PluginTCPClient('localhost')
    assert c.channel is not None
    assert c.channel._channel.target() == b'localhost'
