
import asynctest
import pytest
import ujson
from sanic.response import HTTPResponse

import synse_server
from synse_server.api import http


class TestCoreTest:
    """Tests for the Synse core API 'test' route."""

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
    def test_methods_not_allowed(self, synse_app, method):
        fn = getattr(synse_app.test_client, method)
        response = fn('/test', gather_request=False)
        assert response.status == 405

    @pytest.mark.asyncio
    async def test_ok(self, mocker, make_request):
        # Mock test data
        mocker.patch(
            'synse_server.utils.rfc3339now',
            return_value='2019-04-22T13:30:00Z',
        )

        # --- Test case -----------------------------
        resp = await http.test(make_request('/test'))
        assert isinstance(resp, HTTPResponse)
        assert resp.status == 200

        body = ujson.loads(resp.body)
        assert body == {
            'status': 'ok',
            'timestamp': '2019-04-22T13:30:00Z',
        }


class TestCoreVersion:
    """Tests for the Synse core API 'version' route."""

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
    def test_methods_not_allowed(self, synse_app, method):
        fn = getattr(synse_app.test_client, method)
        response = fn('/version', gather_request=False)
        assert response.status == 405

    @pytest.mark.asyncio
    async def test_ok(self, make_request):
        resp = await http.version(make_request('/version'))
        assert isinstance(resp, HTTPResponse)
        assert resp.status == 200

        body = ujson.loads(resp.body)
        assert body == {
            'version': synse_server.__version__,
            'api_version': synse_server.__api_version__,
        }


class TestV3Config:
    """Tests for the Synse v3 API 'config' route."""

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
    def test_methods_not_allowed(self, synse_app, method):
        fn = getattr(synse_app.test_client, method)
        response = fn('/v3/config', gather_request=False)
        assert response.status == 405

    @pytest.mark.asyncio
    async def test_ok(self, mocker, make_request):
        # Mock test data
        mocker.patch.dict(
            'synse_server.config.options._full_config', {
                'logging': 'debug',
                'plugins': {
                    'tcp': [
                        'localhost:5001'
                    ],
                }
            }
        )

        # --- Test case -----------------------------
        resp = await http.config(make_request('/v3/config'))
        assert isinstance(resp, HTTPResponse)
        assert resp.status == 200

        body = ujson.loads(resp.body)
        assert body == {
            'logging': 'debug',
            'plugins': {
                'tcp': [
                    'localhost:5001'
                ],
            }
        }

    @pytest.mark.asyncio
    async def test_error(self, make_request):
        with asynctest.patch('synse_server.cmd.config') as mock_cmd:
            mock_cmd.side_effect = ValueError()

            with pytest.raises(ValueError):
                await http.config(make_request('/v3/config'))

        mock_cmd.assert_called_once()


class TestV3Plugins:
    """Tests for the Synse v3 API 'plugins' route."""

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
    def test_methods_not_allowed(self, synse_app, method):
        fn = getattr(synse_app.test_client, method)
        response = fn('/v3/plugin', gather_request=False)
        assert response.status == 405

    @pytest.mark.asyncio
    async def test_ok(self, make_request):
        with asynctest.patch('synse_server.cmd.plugins') as mock_plugins:
            mock_plugins.return_value = [
                {
                    "description": "a plugin with emulated devices and data",
                    "id": "12835beffd3e6c603aa4dd92127707b5",
                    "name": "emulator plugin",
                    "maintainer": "vapor io",
                    "active": True
                },
                {
                    "description": "a custom third party plugin",
                    "id": "12835beffd3e6c603aa4dd92127707b6",
                    "name": "custom-plugin",
                    "maintainer": "third-party",
                    "active": True
                },
            ]

            resp = await http.plugins(make_request('/v3/plugins'))
            assert isinstance(resp, HTTPResponse)
            assert resp.status == 200

            body = ujson.loads(resp.body)
            assert body == mock_plugins.return_value

    @pytest.mark.asyncio
    async def test_error(self):
        pass


class TestV3Plugin:
    """Tests for the Synse v3 API 'plugin' route."""

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
    def test_methods_not_allowed(self, synse_app, method):
        fn = getattr(synse_app.test_client, method)
        response = fn('/v3/plugin/123', gather_request=False)
        assert response.status == 405

    @pytest.mark.asyncio
    async def test_ok(self, make_request):
        pass

    @pytest.mark.asyncio
    async def test_not_found(self, make_request):
        pass

    @pytest.mark.asyncio
    async def test_error(self, make_request):
        pass


class TestV3PluginHealth:
    """Tests for the Synse v3 API 'plugin health' route."""

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
    def test_health_methods_not_allowed(self, synse_app, method):
        fn = getattr(synse_app.test_client, method)
        response = fn('/v3/plugin/health', gather_request=False)
        assert response.status == 405

    @pytest.mark.asyncio
    async def test_ok(self):
        pass

    @pytest.mark.asyncio
    async def test_error(self):
        pass


class TestV3Scan:
    """Tests for the Synse v3 API 'scan' route."""

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
    def test_methods_not_allowed(self, synse_app, method):
        fn = getattr(synse_app.test_client, method)
        response = fn('/v3/scan', gather_request=False)
        assert response.status == 405

    @pytest.mark.asyncio
    async def test_ok(self):
        pass

    @pytest.mark.asyncio
    async def test_error(self):
        pass

    @pytest.mark.asyncio
    async def test_invalid_multiple_ns(self):
        pass

    @pytest.mark.asyncio
    async def test_invalid_multiple_sort(self):
        pass

    @pytest.mark.asyncio
    async def test_param_force(self):
        pass

    @pytest.mark.asyncio
    async def test_param_tags(self):
        pass


class TestV3Tags:
    """Tests for the Synse v3 API 'tags' route."""

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
    def test_methods_not_allowed(self, synse_app, method):
        fn = getattr(synse_app.test_client, method)
        response = fn('/v3/tags', gather_request=False)
        assert response.status == 405

    @pytest.mark.asyncio
    async def test_ok(self):
        pass

    @pytest.mark.asyncio
    async def test_error(self):
        pass

    @pytest.mark.asyncio
    async def test_param_ns(self):
        pass

    @pytest.mark.asyncio
    async def test_param_ids(self):
        pass


class TestV3Info:
    """Tests for the Synse v3 API 'info' route."""

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
    def test_methods_not_allowed(self, synse_app, method):
        fn = getattr(synse_app.test_client, method)
        response = fn('/v3/info/123', gather_request=False)
        assert response.status == 405

    @pytest.mark.asyncio
    async def test_ok(self):
        pass

    @pytest.mark.asyncio
    async def test_error(self):
        pass

    @pytest.mark.asyncio
    async def test_not_found(self):
        pass


class TestV3Read:
    """Tests for the Synse v3 API 'read' route."""

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
    def test_methods_not_allowed(self, synse_app, method):
        fn = getattr(synse_app.test_client, method)
        response = fn('/v3/read', gather_request=False)
        assert response.status == 405

    @pytest.mark.asyncio
    async def test_ok(self):
        pass

    @pytest.mark.asyncio
    async def test_error(self):
        pass

    @pytest.mark.asyncio
    async def test_invalid_multiple_ns(self):
        pass

    @pytest.mark.asyncio
    async def test_param_tags(self):
        pass


class TestV3ReadCache:
    """Tests for the Synse v3 API 'read cache' route."""

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
    def test_methods_not_allowed(self, synse_app, method):
        fn = getattr(synse_app.test_client, method)
        response = fn('/v3/readcache', gather_request=False)
        assert response.status == 405

    @pytest.mark.asyncio
    async def test_ok(self):
        pass

    @pytest.mark.asyncio
    async def test_error(self):
        pass

    @pytest.mark.asyncio
    async def test_invalid_multiple_start(self):
        pass

    @pytest.mark.asyncio
    async def test_invalid_multiple_end(self):
        pass


class TestV3ReadDevice:
    """Tests for the Synse v3 API 'read device' route."""

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
    def test_methods_not_allowed(self, synse_app, method):
        fn = getattr(synse_app.test_client, method)
        response = fn('/v3/read/123', gather_request=False)
        assert response.status == 405

    @pytest.mark.asyncio
    async def test_ok(self):
        pass

    @pytest.mark.asyncio
    async def test_error(self):
        pass

    @pytest.mark.asyncio
    async def test_not_found(self):
        pass

    @pytest.mark.asyncio
    async def test_read_not_supported(self):
        pass


class TestV3AsyncWrite:
    """Tests for the Synse v3 API 'async write' route."""

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
    def test_methods_not_allowed(self, synse_app, method):
        fn = getattr(synse_app.test_client, method)
        response = fn('/v3/write/123', gather_request=False)
        assert response.status == 405

    @pytest.mark.asyncio
    async def test_ok(self):
        pass

    @pytest.mark.asyncio
    async def test_error(self):
        pass

    @pytest.mark.asyncio
    async def test_invalid_json(self):
        pass

    @pytest.mark.asyncio
    async def test_invalid_json_missing_key(self):
        pass

    @pytest.mark.asyncio
    async def test_not_found(self):
        pass

    @pytest.mark.asyncio
    async def test_write_not_supported(self):
        pass


class TestV3SyncWrite:
    """Tests for the Synse v3 API 'sync write' route."""

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
    def test_methods_not_allowed(self, synse_app, method):
        fn = getattr(synse_app.test_client, method)
        response = fn('/v3/write/wait/123', gather_request=False)
        assert response.status == 405

    @pytest.mark.asyncio
    async def test_ok(self):
        pass

    @pytest.mark.asyncio
    async def test_error(self):
        pass

    @pytest.mark.asyncio
    async def test_invalid_json(self):
        pass

    @pytest.mark.asyncio
    async def test_invalid_json_missing_key(self):
        pass

    @pytest.mark.asyncio
    async def test_not_found(self):
        pass

    @pytest.mark.asyncio
    async def test_write_not_supported(self):
        pass


class TestV3Transactions:
    """Tests for the Synse v3 API 'transactions' route."""

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
    def test_methods_not_allowed(self, synse_app, method):
        fn = getattr(synse_app.test_client, method)
        response = fn('/v3/transaction', gather_request=False)
        assert response.status == 405

    @pytest.mark.asyncio
    async def test_ok(self):
        pass

    @pytest.mark.asyncio
    async def test_error(self):
        pass


class TestV3Transaction:
    """Test for the Synse v3 API 'transaction' route."""

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
    def test_methods_not_allowed(self, synse_app, method):
        fn = getattr(synse_app.test_client, method)
        response = fn('/v3/transaction/123', gather_request=False)
        assert response.status == 405

    @pytest.mark.asyncio
    async def test_ok(self):
        pass

    @pytest.mark.asyncio
    async def test_error(self):
        pass

    @pytest.mark.asyncio
    async def test_not_found(self):
        pass


class TestV3Device:
    """Test for the Synse v3 API 'device' route."""

    @pytest.mark.parametrize(
        'method', (
            'put',
            'delete',
            'patch',
            'head',
            'options',
        )
    )
    def test_not_allowed(self, synse_app, method):
        fn = getattr(synse_app.test_client, method)
        response = fn('/v3/device/123', gather_request=False)
        assert response.status == 405

    @pytest.mark.asyncio
    async def test_read_ok(self):
        pass

    @pytest.mark.asyncio
    async def test_read_error(self):
        pass

    @pytest.mark.asyncio
    async def test_read_not_found(self):
        pass

    @pytest.mark.asyncio
    async def test_read_not_supported(self):
        pass

    @pytest.mark.asyncio
    async def test_write_ok(self):
        pass

    @pytest.mark.asyncio
    async def test_write_error(self):
        pass

    @pytest.mark.asyncio
    async def test_write_invalid_json(self):
        pass

    @pytest.mark.asyncio
    async def test_write_invalid_json_missing_key(self):
        pass

    @pytest.mark.asyncio
    async def test_write_not_found(self):
        pass

    @pytest.mark.asyncio
    async def test_write_not_supported(self):
        pass
