
import pytest
from synse_grpc import api, client

from synse_server import errors
from synse_server.cmd import plugin
from synse_server.plugin import Plugin


@pytest.mark.asyncio
async def test_plugin_not_found(mocker):
    # Mock test data
    mock_get = mocker.patch('synse_server.plugin.manager.get', return_value=None)

    # --- Test case -----------------------------
    plugin_id = '123456'

    with pytest.raises(errors.NotFound):
        await plugin.plugin(plugin_id)

    mock_get.assert_called_once()
    mock_get.assert_called_with(plugin_id)


@pytest.mark.asyncio
async def test_plugin_client_error(mocker):
    # Mock test data
    mock_get = mocker.patch(
        'synse_server.plugin.manager.get',
        return_value=Plugin(
            info={'id': '123456', 'tag': 'test-plugin'},
            version={},
            client=client.PluginClientV3('localhost:5001', 'tcp'),
        ),
    )
    mock_health = mocker.patch(
        'synse_grpc.client.PluginClientV3.health',
        side_effect=ValueError(),
    )

    # --- Test case -----------------------------
    plugin_id = '123456'

    with pytest.raises(errors.ServerError):
        await plugin.plugin(plugin_id)

    mock_get.assert_called_once()
    mock_get.assert_called_with(plugin_id)
    mock_health.assert_called_once()


@pytest.mark.asyncio
async def test_plugin_ok(mocker, simple_plugin):
    # Mock test data
    mocker.patch.dict('synse_server.plugin.manager.plugins', {
        '123': simple_plugin,
    })
    mock_health = mocker.patch(
        'synse_grpc.client.PluginClientV3.health',
        return_value=api.V3Health(
            timestamp='2019-04-22T13:30:00Z',
            status=api.OK,
            checks=[],
        ),
    )
    mock_refresh = mocker.patch(
        'synse_server.plugin.manager.refresh',
    )

    # --- Test case -----------------------------
    plugin_id = '123'

    resp = await plugin.plugin(plugin_id)
    assert resp == {
        'id': '123',  # from simple_plugin fixture
        'tag': 'test/foo',  # from simple_plugin fixture
        'vcs': 'https://github.com/vapor-ware/synse-server',  # from simple_plugin fixture
        'active': True,
        'network': {  # from simple_plugin fixture
            'address': 'localhost:5432',
            'protocol': 'tcp',
        },
        'version': {},  # from simple_plugin fixture
        'health': {
            'timestamp': '2019-04-22T13:30:00Z',
            'status': 'OK',
            'checks': [],
        }
    }

    mock_health.assert_called_once()
    mock_refresh.assert_not_called()


@pytest.mark.asyncio
async def test_plugin_ok_refresh(mocker, simple_plugin):
    # Mock test data
    mock_get = mocker.patch(
        'synse_server.plugin.manager.get',
        return_value=simple_plugin,
    )
    mock_health = mocker.patch(
        'synse_grpc.client.PluginClientV3.health',
        return_value=api.V3Health(
            timestamp='2019-04-22T13:30:00Z',
            status=api.OK,
            checks=[],
        ),
    )
    mock_refresh = mocker.patch(
        'synse_server.plugin.manager.refresh',
    )

    # --- Test case -----------------------------
    plugin_id = '123'

    resp = await plugin.plugin(plugin_id)
    assert resp == {
        'id': '123',  # from simple_plugin fixture
        'tag': 'test/foo',  # from simple_plugin fixture
        'vcs': 'https://github.com/vapor-ware/synse-server',  # from simple_plugin fixture
        'active': True,
        'network': {  # from simple_plugin fixture
            'address': 'localhost:5432',
            'protocol': 'tcp',
        },
        'version': {},  # from simple_plugin fixture
        'health': {
            'timestamp': '2019-04-22T13:30:00Z',
            'status': 'OK',
            'checks': [],
        }
    }

    mock_get.assert_called_once()
    mock_get.assert_called_with(plugin_id)
    mock_health.assert_called_once()
    mock_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_plugins_no_plugin(mocker):
    # Mock test data
    mocker.patch.dict('synse_server.plugin.manager.plugins', {})
    mock_refresh = mocker.patch(
        'synse_server.plugin.manager.refresh',
    )

    # --- Test case -----------------------------
    resp = await plugin.plugins()
    assert resp == []

    mock_refresh.assert_called_once()


@pytest.mark.asyncio
async def test_plugins_ok(mocker, simple_plugin):
    # Mock test data
    mocker.patch.dict('synse_server.plugin.manager.plugins', {
        '123': simple_plugin,
    })
    mock_refresh = mocker.patch(
        'synse_server.plugin.manager.refresh',
    )

    # --- Test case -----------------------------
    resp = await plugin.plugins()
    assert resp == [
        {  # from simple_plugin fixture
            'id': '123',
            'tag': 'test/foo',
            'active': False,
        },
    ]

    mock_refresh.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.usefixtures('patch_utils_rfc3339now')
async def test_plugin_health_no_plugins(mocker):
    # Mock test data
    mocker.patch.dict('synse_server.plugin.manager.plugins', {})
    mock_refresh = mocker.patch(
        'synse_server.plugin.manager.refresh',
    )

    # --- Test case -----------------------------
    resp = await plugin.plugin_health()
    assert resp == {
        'status': 'healthy',
        'updated': '2019-04-22T13:30:00Z',  # from fixture: patch_utils_rfc3339now
        'healthy': [],
        'unhealthy': [],
        'active': 0,
        'inactive': 0,
    }

    mock_refresh.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.usefixtures('patch_utils_rfc3339now')
async def test_plugin_health_healthy(mocker, simple_plugin):
    # Mock test data
    mocker.patch.dict('synse_server.plugin.manager.plugins', {
        '123': simple_plugin,
    })
    mock_health = mocker.patch(
        'synse_grpc.client.PluginClientV3.health',
        return_value=api.V3Health(
            timestamp='2019-04-22T13:30:00Z',
            status=api.OK,
            checks=[],
        ),
    )
    mock_refresh = mocker.patch(
        'synse_server.plugin.manager.refresh',
    )

    # --- Test case -----------------------------
    resp = await plugin.plugin_health()
    assert resp == {
        'status': 'healthy',
        'updated': '2019-04-22T13:30:00Z',  # from fixture: patch_utils_rfc3339now
        'healthy': ['123'],
        'unhealthy': [],
        'active': 1,
        'inactive': 0,
    }

    mock_health.assert_called_once()
    mock_refresh.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.usefixtures('patch_utils_rfc3339now')
async def test_plugin_health_unhealthy(mocker, simple_plugin):
    # Mock test data
    mocker.patch.dict('synse_server.plugin.manager.plugins', {
        '123': simple_plugin,
    })
    mock_health = mocker.patch(
        'synse_grpc.client.PluginClientV3.health',
        return_value=api.V3Health(
            timestamp='2019-04-22T13:30:00Z',
            status=api.FAILING,
            checks=[],
        ),
    )
    mock_refresh = mocker.patch(
        'synse_server.plugin.manager.refresh',
    )

    # --- Test case -----------------------------
    resp = await plugin.plugin_health()
    assert resp == {
        'status': 'unhealthy',
        'updated': '2019-04-22T13:30:00Z',  # from fixture: patch_utils_rfc3339now
        'healthy': [],
        'unhealthy': ['123'],
        'active': 1,
        'inactive': 0,
    }

    mock_health.assert_called_once()
    mock_refresh.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.usefixtures('patch_utils_rfc3339now')
async def test_plugin_health_inactive(mocker, simple_plugin):
    # Mock test data
    mocker.patch.dict('synse_server.plugin.manager.plugins', {
        '123': simple_plugin,
    })
    mock_health = mocker.patch(
        'synse_grpc.client.PluginClientV3.health',
        side_effect=ValueError(),
    )
    mock_refresh = mocker.patch(
        'synse_server.plugin.manager.refresh',
    )

    # --- Test case -----------------------------
    resp = await plugin.plugin_health()

    assert resp == {
        'status': 'unhealthy',
        'updated': '2019-04-22T13:30:00Z',  # from fixture: patch_utils_rfc3339now
        'healthy': [],
        'unhealthy': [],
        'active': 0,
        'inactive': 1,
    }

    mock_health.assert_called_once()
    mock_refresh.assert_not_called()
