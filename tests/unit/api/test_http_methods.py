
import pytest


@pytest.mark.parametrize(
    'method', (
        'post',
        'put',
        'delete',
        'patch',
        'head',
        'options',
    )
)
def test_test_methods_not_allowed(synse_app, method):
    fn = getattr(synse_app.test_client, method)
    response = fn('/test', gather_request=False)
    assert response.status == 405


@pytest.mark.parametrize(
    'method', (
        'post',
        'put',
        'delete',
        'patch',
        'head',
        'options',
    )
)
def test_version_methods_not_allowed(synse_app, method):
    fn = getattr(synse_app.test_client, method)
    response = fn('/version', gather_request=False)
    assert response.status == 405


@pytest.mark.parametrize(
    'method', (
        'post',
        'put',
        'delete',
        'patch',
        'head',
        'options',
    )
)
def test_config_methods_not_allowed(synse_app, method):
    fn = getattr(synse_app.test_client, method)
    response = fn('/v3/config', gather_request=False)
    assert response.status == 405


@pytest.mark.parametrize(
    'method', (
        'post',
        'put',
        'delete',
        'patch',
        'head',
        'options',
    )
)
def test_plugins_methods_not_allowed(synse_app, method):
    fn = getattr(synse_app.test_client, method)
    response = fn('/v3/plugin', gather_request=False)
    assert response.status == 405


@pytest.mark.parametrize(
    'method', (
        'post',
        'put',
        'delete',
        'patch',
        'head',
        'options',
    )
)
def test_plugin_methods_not_allowed(synse_app, method):
    fn = getattr(synse_app.test_client, method)
    response = fn('/v3/plugin/123', gather_request=False)
    assert response.status == 405


@pytest.mark.parametrize(
    'method', (
        'post',
        'put',
        'delete',
        'patch',
        'head',
        'options',
    )
)
def test_plugin_health_methods_not_allowed(synse_app, method):
    fn = getattr(synse_app.test_client, method)
    response = fn('/v3/plugin/health', gather_request=False)
    assert response.status == 405


@pytest.mark.parametrize(
    'method', (
        'post',
        'put',
        'delete',
        'patch',
        'head',
        'options',
    )
)
def test_scan_methods_not_allowed(synse_app, method):
    fn = getattr(synse_app.test_client, method)
    response = fn('/v3/scan', gather_request=False)
    assert response.status == 405


@pytest.mark.parametrize(
    'method', (
        'post',
        'put',
        'delete',
        'patch',
        'head',
        'options',
    )
)
def test_tags_methods_not_allowed(synse_app, method):
    fn = getattr(synse_app.test_client, method)
    response = fn('/v3/tags', gather_request=False)
    assert response.status == 405


@pytest.mark.parametrize(
    'method', (
        'post',
        'put',
        'delete',
        'patch',
        'head',
        'options',
    )
)
def test_info_methods_not_allowed(synse_app, method):
    fn = getattr(synse_app.test_client, method)
    response = fn('/v3/info/123', gather_request=False)
    assert response.status == 405


@pytest.mark.parametrize(
    'method', (
        'post',
        'put',
        'delete',
        'patch',
        'head',
        'options',
    )
)
def test_read_methods_not_allowed(synse_app, method):
    fn = getattr(synse_app.test_client, method)
    response = fn('/v3/read', gather_request=False)
    assert response.status == 405


@pytest.mark.parametrize(
    'method', (
        'post',
        'put',
        'delete',
        'patch',
        'head',
        'options',
    )
)
def test_readcache_methods_not_allowed(synse_app, method):
    fn = getattr(synse_app.test_client, method)
    response = fn('/v3/readcache', gather_request=False)
    assert response.status == 405


@pytest.mark.parametrize(
    'method', (
        'post',
        'put',
        'delete',
        'patch',
        'head',
        'options',
    )
)
def test_read_device_methods_not_allowed(synse_app, method):
    fn = getattr(synse_app.test_client, method)
    response = fn('/v3/read/123', gather_request=False)
    assert response.status == 405


@pytest.mark.parametrize(
    'method', (
        'get',
        'put',
        'delete',
        'patch',
        'head',
        'options',
    )
)
def test_async_write_methods_not_allowed(synse_app, method):
    fn = getattr(synse_app.test_client, method)
    response = fn('/v3/write/123', gather_request=False)
    assert response.status == 405


@pytest.mark.parametrize(
    'method', (
        'get',
        'put',
        'delete',
        'patch',
        'head',
        'options',
    )
)
def test_sync_write_methods_not_allowed(synse_app, method):
    fn = getattr(synse_app.test_client, method)
    response = fn('/v3/write/wait/123', gather_request=False)
    assert response.status == 405


@pytest.mark.parametrize(
    'method', (
        'post',
        'put',
        'delete',
        'patch',
        'head',
        'options',
    )
)
def test_transactions_methods_not_allowed(synse_app, method):
    fn = getattr(synse_app.test_client, method)
    response = fn('/v3/transaction', gather_request=False)
    assert response.status == 405


@pytest.mark.parametrize(
    'method', (
        'post',
        'put',
        'delete',
        'patch',
        'head',
        'options',
    )
)
def test_transaction_methods_not_allowed(synse_app, method):
    fn = getattr(synse_app.test_client, method)
    response = fn('/v3/transaction/123', gather_request=False)
    assert response.status == 405


@pytest.mark.parametrize(
    'method', (
        'put',
        'delete',
        'patch',
        'head',
        'options',
    )
)
def test_device_methods_not_allowed(synse_app, method):
    fn = getattr(synse_app.test_client, method)
    response = fn('/v3/device/123', gather_request=False)
    assert response.status == 405
