
from unittest import mock

import pytest
from synse_grpc import client

from synse_server.cmd import plugin
from synse_server import errors
from synse_server.plugin import Plugin


@pytest.mark.asyncio
async def test_plugin_not_found(patch_get):
    #patch_get = mock.patch('synse_server.plugin.manager.get', return_value=None)
    print(type(patch_get))

    plugin_id = '123456'

    #print('patch_get -------')
    #print(patch_get)

    with pytest.raises(errors.NotFound):
        await plugin.plugin(plugin_id)

    patch_get.assert_called_once()
    patch_get.assert_called_with(plugin_id)


@pytest.mark.asyncio
@mock.patch(
    'synse_grpc.client.PluginClientV3.health',
    side_effect=ValueError(),
)
@mock.patch(
    'synse_server.plugin.manager.get',
    return_value=Plugin(
        info={'id': '123456', 'tag': 'test-plugin'},
        version={},
        client=client.PluginClientV3('localhost:5001', 'tcp'),
    ),
)
async def test_plugin_client_error(patch_get, patch_health):
    print(type(patch_get))
    plugin_id = '123456'

    with pytest.raises(errors.ServerError):
        await plugin.plugin(plugin_id)

    patch_get.assert_called_once()
    patch_get.assert_called_with(plugin_id)
    patch_health.assert_called_once()


@pytest.mark.asyncio
async def test_plugin_ok():
    pass


@pytest.mark.asyncio
async def test_plugin_ok_refresh():
    pass


@pytest.mark.asyncio
async def test_plugins_no_plugin():
    pass


@pytest.mark.asyncio
async def test_plugins_ok():
    pass


@pytest.mark.asyncio
async def test_plugins_ok_refresh():
    pass


@pytest.mark.asyncio
async def test_plugin_health_no_plugins():
    pass


@pytest.mark.asyncio
async def test_plugin_health_healthy():
    pass


@pytest.mark.asyncio
async def test_plugin_health_unhealthy():
    pass


@pytest.mark.asyncio
async def test_plugin_health_ok():
    pass


@pytest.mark.asyncio
async def test_plugin_health_ok_refresh():
    pass
