
import asynctest
import pytest
import ujson

from synse_server import errors


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


@pytest.mark.usefixtures('patch_utils_rfc3339now')
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


@pytest.mark.usefixtures('patch_utils_rfc3339now')
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

    def test_ok(self, synse_app):
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

            resp = synse_app.test_client.get('/v3/plugin', gather_request=False)
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()

    def test_error(self, synse_app):
        with asynctest.patch('synse_server.cmd.plugins') as mock_cmd:
            mock_cmd.side_effect = ValueError('***********')

            resp = synse_app.test_client.get('/v3/plugin', gather_request=False)
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


@pytest.mark.usefixtures('patch_utils_rfc3339now')
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

    def test_ok(self, synse_app):
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

            resp = synse_app.test_client.get('/v3/plugin/12345', gather_request=False)
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with('12345')

    def test_not_found(self, synse_app):
        with asynctest.patch('synse_server.cmd.plugin') as mock_cmd:
            mock_cmd.side_effect = errors.NotFound('plugin not found')

            resp = synse_app.test_client.get('/v3/plugin/123', gather_request=False)
            assert resp.status == 404
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'plugin not found',
                'description': 'resource not found',
                'http_code': 404,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with('123')

    def test_error(self, synse_app):
        with asynctest.patch('synse_server.cmd.plugin') as mock_cmd:
            mock_cmd.side_effect = ValueError('***********')

            resp = synse_app.test_client.get('/v3/plugin/123', gather_request=False)
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
        mock_cmd.assert_called_with('123')


@pytest.mark.usefixtures('patch_utils_rfc3339now')
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

    def test_ok(self):
        pass

    def test_error(self, synse_app):
        with asynctest.patch('synse_server.cmd.plugin_health') as mock_cmd:
            mock_cmd.side_effect = ValueError('***********')

            resp = synse_app.test_client.get('/v3/plugin/health', gather_request=False)
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


@pytest.mark.usefixtures('patch_utils_rfc3339now')
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

    def test_ok(self):
        pass

    def test_error(self, synse_app):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            mock_cmd.side_effect = ValueError('***********')

            resp = synse_app.test_client.get('/v3/scan', gather_request=False)
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
        mock_cmd.assert_called_with(
            ns='default',
            tags=[],
            force=False,
            sort='plugin,sortIndex,id',
        )

    def test_invalid_multiple_ns(self):
        pass

    def test_invalid_multiple_sort(self):
        pass

    def test_param_force(self):
        pass

    def test_param_tags(self):
        pass


@pytest.mark.usefixtures('patch_utils_rfc3339now')
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

    def test_ok(self):
        pass

    def test_error(self, synse_app):
        with asynctest.patch('synse_server.cmd.tags') as mock_cmd:
            mock_cmd.side_effect = ValueError('***********')

            resp = synse_app.test_client.get('/v3/tags', gather_request=False)
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
        mock_cmd.assert_called_with(
            with_id_tags=False
        )

    def test_param_ns(self):
        pass

    def test_param_ids(self):
        pass


@pytest.mark.usefixtures('patch_utils_rfc3339now')
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

    def test_ok(self):
        pass

    def test_error(self, synse_app):
        with asynctest.patch('synse_server.cmd.info') as mock_cmd:
            mock_cmd.side_effect = ValueError('***********')

            resp = synse_app.test_client.get('/v3/info/123', gather_request=False)
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
        mock_cmd.assert_called_with('123')

    def test_not_found(self):
        pass


@pytest.mark.usefixtures('patch_utils_rfc3339now')
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

    def test_ok(self):
        pass

    def test_error(self, synse_app):
        with asynctest.patch('synse_server.cmd.read') as mock_cmd:
            mock_cmd.side_effect = ValueError('***********')

            resp = synse_app.test_client.get('/v3/read', gather_request=False)
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
        mock_cmd.assert_called_with(
            ns='default',
            tags=[],
        )

    def test_invalid_multiple_ns(self):
        pass

    def test_param_tags(self):
        pass


@pytest.mark.usefixtures('patch_utils_rfc3339now')
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

    def test_ok(self):
        pass

    # def test_error(self, synse_app):
    #     with asynctest.patch('synse_server.cmd.read_cache') as mock_cmd:
    #         mock_cmd.side_effect = ValueError('***********')
    #
    #         resp = synse_app.test_client.get('/v3/readcache', gather_request=False)
    #         assert resp.status == 500
    #         assert resp.headers['Content-Type'] == 'application/json'
    #
    #         body = ujson.loads(resp.body)
    #         assert body == {
    #             'context': '***********',
    #             'description': 'an unexpected error occurred',
    #             'http_code': 500,
    #             'timestamp': '2019-04-22T13:30:00Z',
    #         }
    #
    #     mock_cmd.assert_called_once()
    #     mock_cmd.assert_called_with('', '')

    def test_invalid_multiple_start(self):
        pass

    def test_invalid_multiple_end(self):
        pass


@pytest.mark.usefixtures('patch_utils_rfc3339now')
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

    def test_ok(self):
        pass

    def test_error(self, synse_app):
        with asynctest.patch('synse_server.cmd.read_device') as mock_cmd:
            mock_cmd.side_effect = ValueError('***********')

            resp = synse_app.test_client.get('/v3/read/123', gather_request=False)
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
        mock_cmd.assert_called_with('123')

    def test_not_found(self):
        pass

    def test_read_not_supported(self):
        pass


@pytest.mark.usefixtures('patch_utils_rfc3339now')
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

    def test_ok(self):
        pass

    def test_error(self, synse_app):
        with asynctest.patch('synse_server.cmd.write_async') as mock_cmd:
            mock_cmd.side_effect = ValueError('***********')

            resp = synse_app.test_client.post(
                '/v3/write/123',
                data=ujson.dumps({'action': 'foo', 'data': 'bar'}),
                gather_request=False,
            )
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
        mock_cmd.assert_called_with(
            device_id='123',
            payload=[{'action': 'foo', 'data': 'bar'}],
        )

    def test_invalid_json(self):
        pass

    def test_invalid_json_missing_key(self):
        pass

    def test_not_found(self):
        pass

    def test_write_not_supported(self):
        pass


@pytest.mark.usefixtures('patch_utils_rfc3339now')
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

    def test_ok(self):
        pass

    def test_error(self, synse_app):
        with asynctest.patch('synse_server.cmd.write_sync') as mock_cmd:
            mock_cmd.side_effect = ValueError('***********')

            resp = synse_app.test_client.post(
                '/v3/write/wait/123',
                data=ujson.dumps({'action': 'foo', 'data': 'bar'}),
                gather_request=False,
            )
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
        mock_cmd.assert_called_with(
            device_id='123',
            payload=[{'action': 'foo', 'data': 'bar'}]
        )

    def test_invalid_json(self):
        pass

    def test_invalid_json_missing_key(self):
        pass

    def test_not_found(self):
        pass

    def test_write_not_supported(self):
        pass


@pytest.mark.usefixtures('patch_utils_rfc3339now')
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

    def test_ok(self):
        pass

    def test_error(self, synse_app):
        with asynctest.patch('synse_server.cmd.transactions') as mock_cmd:
            mock_cmd.side_effect = ValueError('***********')

            resp = synse_app.test_client.get('/v3/transaction', gather_request=False)
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


@pytest.mark.usefixtures('patch_utils_rfc3339now')
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

    def test_ok(self):
        pass

    def test_error(self, synse_app):
        with asynctest.patch('synse_server.cmd.transaction') as mock_cmd:
            mock_cmd.side_effect = ValueError('***********')

            resp = synse_app.test_client.get('/v3/transaction/123', gather_request=False)
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
        mock_cmd.assert_called_with('123')

    def test_not_found(self):
        pass


@pytest.mark.usefixtures('patch_utils_rfc3339now')
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

    def test_read_ok(self):
        pass

    def test_read_error(self, synse_app):
        with asynctest.patch('synse_server.cmd.read_device') as mock_cmd:
            mock_cmd.side_effect = ValueError('***********')

            resp = synse_app.test_client.get('/v3/device/123', gather_request=False)
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
        mock_cmd.assert_called_with('123')

    def test_read_not_found(self):
        pass

    def test_read_not_supported(self):
        pass

    def test_write_ok(self):
        pass

    def test_write_error(self, synse_app):
        with asynctest.patch('synse_server.cmd.write_sync') as mock_cmd:
            mock_cmd.side_effect = ValueError('***********')

            resp = synse_app.test_client.post(
                '/v3/write/wait/123',
                data=ujson.dumps({'action': 'foo', 'data': 'bar'}),
                gather_request=False,
            )
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
        mock_cmd.assert_called_with(
            device_id='123',
            payload=[{'action': 'foo', 'data': 'bar'}]
        )

    def test_write_invalid_json(self):
        pass

    def test_write_invalid_json_missing_key(self):
        pass

    def test_write_not_found(self):
        pass

    def test_write_not_supported(self):
        pass
