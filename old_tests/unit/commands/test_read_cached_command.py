"""Test the 'synse_server.commands.read' Synse Server module."""

import asynctest
import grpc
import pytest
from synse_grpc import api

import synse_server.cache
from synse_server import errors, plugin
from synse_server.commands.read_cache import read_cached
from synse_server.proto.client import PluginClient, PluginTCPClient


@pytest.fixture()
def patch_get_plugins(monkeypatch):
    """Monkeypatch the plugin's 'get_plugins' function."""
    def _mock():
        return 'test', plugin.Plugin(
            metadata=api.Metadata(
                name='test',
                tag='vaporio/test'
            ),
            address='localhost:5001',
            plugin_client=PluginTCPClient(
                address='localhost:5001'
            ),
        )

    mocked = asynctest.CoroutineMock(plugin.get_plugins, side_effect=_mock)
    monkeypatch.setattr(plugin, 'get_plugins', mocked)
    return patch_get_plugins


@pytest.fixture()
def patch_get_device_info(monkeypatch):
    """Monkeypatch getting device info for the test readings."""
    def _mock(*args, **kwargs):
        return 'vaporio/test+tcp@localhost:5001/test', api.Device(
            timestamp='2018-10-18T16:43:18+00:00',
            uid='12345',
            kind='test',
            plugin='test',
            location=api.Location(
                rack='rack',
                board='board',
            ),
            output=[
                api.Output(
                    type='temperature',
                    precision=3,
                    unit=api.Unit(
                        name='celsius',
                        symbol='C'
                    )
                ),
                api.Output(
                    type='humidity',
                    precision=3,
                    unit=api.Unit(
                        name='percent',
                        symbol='%'
                    )
                )
            ]
        )
    mocked = asynctest.CoroutineMock(synse_server.cache.get_device_info, side_effect=_mock)
    monkeypatch.setattr(synse_server.cache, 'get_device_info', mocked)
    return patch_get_device_info


@pytest.fixture()
def add_plugin():
    """Add a test plugin to the plugin manager."""
    p = plugin.Plugin(
        metadata=api.Metadata(
            name='test',
            tag='vaporio/test',
        ),
        address='localhost:5001',
        plugin_client=PluginTCPClient(
            address='localhost:5001',
        ),
    )

    yield

    plugin.Plugin.manager.remove(p.id())


@pytest.fixture()
def clear_manager():
    """Clear the plugin manager state after the test."""
    yield
    plugin.Plugin.manager.plugins = {}


@pytest.mark.asyncio
async def test_read_cached_no_plugins(monkeypatch):
    """Read the plugin cache(s) when there are no plugins configured."""

    assert len(plugin.Plugin.manager.plugins) == 0

    results = [i async for i in read_cached()]
    assert len(results) == 0


@pytest.mark.asyncio
async def test_read_cached_grpc_error(monkeypatch, add_plugin):
    """Read the plugin cache(s) but get back a grpc error."""

    # monkeypatch the read_cached method so it fails with a grpc error
    def _mock(*args, **kwargs):
        raise grpc.RpcError()
    monkeypatch.setattr(PluginClient, 'read_cached', _mock)

    assert len(plugin.Plugin.manager.plugins) == 1
    with pytest.raises(errors.ServerError):
        _ = [i async for i in read_cached()]


@pytest.mark.asyncio
async def test_read_cached_no_data(monkeypatch, add_plugin):
    """Read the plugin cache(s) when there is no data in the cache to get."""

    # monkeypatch the read_cached method so it yields no readings
    def _mock(*args, **kwargs):
        yield
    monkeypatch.setattr(PluginClient, 'read_cached', _mock)

    assert len(plugin.Plugin.manager.plugins) == 1
    results = [i async for i in read_cached()]
    assert len(results) == 0


@pytest.mark.asyncio
async def test_read_cached_command(monkeypatch, patch_get_device_info, add_plugin):
    """Read a plugin cache for an existing plugin."""

    # monkeypatch the read_cached method so it yields some data
    def _mock(*args, **kwargs):
        readings = [
            api.DeviceReading(
                rack='rack',
                board='board',
                device='device',
                reading=api.Reading(
                    timestamp='2018-10-18T16:43:18+00:00',
                    type='temperature',
                    int64_value=10,
                )
            ),
            api.DeviceReading(
                rack='rack',
                board='board',
                device='device',
                reading=api.Reading(
                    timestamp='2018-10-18T16:43:18+00:00',
                    type='humidity',
                    int64_value=30,
                )
            )
        ]
        for r in readings:
            yield r
    monkeypatch.setattr(PluginClient, 'read_cached', _mock)

    assert len(plugin.Plugin.manager.plugins) == 1
    results = [i async for i in read_cached()]
    assert len(results) == 2
    assert results[0].data['type'] == 'temperature'
    assert results[1].data['type'] == 'humidity'


@pytest.mark.asyncio
async def test_read_cached_command_2(monkeypatch, patch_get_device_info, clear_manager):
    """Read the plugin cache for multiple plugins."""

    # Add plugins to the manager (this is done by the constructor)
    plugin.Plugin(
        metadata=api.Metadata(
            name='foo',
            tag='vaporio/foo',
        ),
        address='localhost:5001',
        plugin_client=PluginTCPClient(
            address='localhost:5001',
        ),
    )
    plugin.Plugin(
        metadata=api.Metadata(
            name='bar',
            tag='vaporio/bar',
        ),
        address='localhost:5002',
        plugin_client=PluginTCPClient(
            address='localhost:5002',
        ),
    )

    # monkeypatch the read_cached method so it yields some data
    def _mock(*args, **kwargs):
        readings = [
            api.DeviceReading(
                rack='rack',
                board='board',
                device='device',
                reading=api.Reading(
                    timestamp='2018-10-18T16:43:18+00:00',
                    type='temperature',
                    int64_value=10,
                )
            ),
            api.DeviceReading(
                rack='rack',
                board='board',
                device='device',
                reading=api.Reading(
                    timestamp='2018-10-18T16:43:18+00:00',
                    type='humidity',
                    int64_value=30,
                )
            )
        ]
        for r in readings:
            yield r

    monkeypatch.setattr(PluginClient, 'read_cached', _mock)

    assert len(plugin.Plugin.manager.plugins) == 2
    results = [i async for i in read_cached()]

    # two plugins with two patched readings each
    assert len(results) == 4
    assert results[0].data['type'] == 'temperature'
    assert results[1].data['type'] == 'humidity'
    assert results[2].data['type'] == 'temperature'
    assert results[3].data['type'] == 'humidity'


@pytest.mark.asyncio
async def test_read_cached_command_no_device(monkeypatch, add_plugin):
    """Read a plugin cache for an existing plugin."""

    # monkeypatch the read_cached method so it yields some data
    def _mock_read(*args, **kwargs):
        yield api.DeviceReading(
            rack='rack',
            board='board',
            device='device',
            reading=api.Reading(
                timestamp='2018-10-18T16:43:18+00:00',
                type='temperature',
                int64_value=10,
            )
        )
    monkeypatch.setattr(PluginClient, 'read_cached', _mock_read)

    # monkeypatch get_device_info to raise a DeviceNotFoundError
    def _mock_device(*args, **kwargs):
        raise errors.NotFound('')
    mocked = asynctest.CoroutineMock(synse_server.cache.get_device_info, side_effect=_mock_device)
    monkeypatch.setattr(synse_server.cache, 'get_device_info', mocked)

    assert len(plugin.Plugin.manager.plugins) == 1
    results = [i async for i in read_cached()]
    assert len(results) == 0
