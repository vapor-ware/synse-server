
import asynctest
import pytest
import ujson


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

    def test_ok(self, synse_app):
        with asynctest.patch('synse_server.cmd.test') as mock_cmd:
            mock_cmd.return_value = {
                'status': 'ok',
                'timestamp': '2019-04-22T13:30:00Z',
            }

            resp = synse_app.test_client.get('/test', gather_request=False)
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()


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

    def test_ok(self, synse_app):
        with asynctest.patch('synse_server.cmd.version') as mock_cmd:
            mock_cmd.return_value = {
                'version': '3.0.0',
                'api_version': 'v3',
            }

            resp = synse_app.test_client.get('/version', gather_request=False)
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()


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

    def test_ok(self, synse_app):
        with asynctest.patch('synse_server.cmd.config') as mock_cmd:
            mock_cmd.return_value = {
                'logging': 'debug',
                'plugins': {
                    'tcp': [
                        'localhost:5001'
                    ],
                }
            }

            resp = synse_app.test_client.get('/v3/config', gather_request=False)
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()

    @pytest.mark.usefixtures('patch_utils_rfc3339now')
    def test_error(self, synse_app):
        with asynctest.patch('synse_server.cmd.config') as mock_cmd:
            mock_cmd.side_effect = ValueError('***********')

            resp = synse_app.test_client.get('/v3/config', gather_request=False)
            assert resp.status == 500
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': '***********',
                'description': 'an unexpected error occurred',
                'http_code': 500,
                'timestamp': '2019-04-22T13:30:00Z',
            }

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
        with asynctest.patch('synse_server.cmd.plugins') as mock_cmd:
            mock_cmd.return_value = [
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

            # resp = await http.plugins(make_request('/v3/plugins'))
            # assert isinstance(resp, HTTPResponse)
            # assert resp.status == 200
            #
            # body = ujson.loads(resp.body)
            # assert body == mock_cmd.return_value

    @pytest.mark.asyncio
    async def test_error(self, make_request):
        with asynctest.patch('synse_server.cmd.plugins') as mock_cmd:
            mock_cmd.side_effect = ValueError()

        #     with pytest.raises(ValueError):
        #         await http.config(make_request('/v3/plugin'))
        #
        # mock_cmd.assert_called_once()


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
        with asynctest.patch('synse_server.cmd.plugin') as mock_cmd:
            mock_cmd.return_value = {
                'id': '12345',
                'tag': 'test/plugin',
                'active': True,
                'network': {
                    'address': 'localhost:5001',
                    'protocol': 'tcp',
                },
                'version': {
                    'sdk_version': '3.0',
                },
                'health': {
                    'status': 'OK',
                },
            }

            # resp = await http.plugin(make_request('/v3/plugin/12345'))
            # assert isinstance(resp, HTTPResponse)
            # assert resp.status == 200
            #
            # body = ujson.loads(resp.body)
            # assert body == mock_cmd.return_value

    @pytest.mark.asyncio
    async def test_not_found(self, make_request):
        pass

    @pytest.mark.asyncio
    async def test_error(self, make_request):
        with asynctest.patch('synse_server.cmd.plugin') as mock_cmd:
            mock_cmd.side_effect = ValueError()

        #     with pytest.raises(ValueError):
        #         await http.config(make_request('/v3/plugin/123'))
        #
        # mock_cmd.assert_called_once()
        # mock_cmd.assert_called_with('123')


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
