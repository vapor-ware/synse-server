
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

    def test_ok(self, synse_app):
        with asynctest.patch('synse_server.cmd.plugin_health') as mock_cmd:
            mock_cmd.return_value = {
                'status': 'healthy',
                'updated': '2019-04-22T13:30:00Z',
                'healthy': [
                    '123',
                ],
                'unhealthy': [
                    '456',
                ],
                'active': 1,
                'inactive': 1,
            }

            resp = synse_app.test_client.get('/v3/plugin/health', gather_request=False)
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()

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

    def test_ok(self, synse_app):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            mock_cmd.return_value = [
                {
                    'id': '12345',
                    'info': 'foo',
                    'type': 'temperature',
                    'plugin': 'plugin-1',
                    'tags': [
                        'default/foo:bar',
                    ],
                },
                {
                    'id': '54321',
                    'info': 'bar',
                    'type': 'temperature',
                    'plugin': 'plugin-2',
                    'tags': [
                        'default/foo:bar',
                    ],
                },
            ]

            resp = synse_app.test_client.get('/v3/scan', gather_request=False)
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tag_groups=[],
            force=False,
            sort='plugin,sortIndex,id',
        )

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
            tag_groups=[],
            force=False,
            sort='plugin,sortIndex,id',
        )

    def test_invalid_multiple_ns(self, synse_app):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:

            resp = synse_app.test_client.get('/v3/scan?ns=ns-1&ns=ns-2', gather_request=False)
            assert resp.status == 400
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'invalid parameter: only one namespace may be specified',
                'description': 'invalid user input',
                'http_code': 400,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_not_called()

    def test_invalid_multiple_sort(self, synse_app):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:

            resp = synse_app.test_client.get('/v3/scan?sort=id&sort=type', gather_request=False)
            assert resp.status == 400
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'invalid parameter: only one sort key may be specified',
                'description': 'invalid user input',
                'http_code': 400,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_not_called()

    @pytest.mark.parametrize(
        'qparam,expected', [
            ('?ns=', 'default'),
            ('?ns=default', 'default'),
            ('?ns=foo', 'foo'),
            ('?ns=test', 'test'),
            ('?ns=TEST', 'TEST'),
            ('?ns=t.e.s.t', 't.e.s.t'),
        ]
    )
    def test_param_ns(self, synse_app, qparam, expected):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            mock_cmd.return_value = [
                {
                    'id': '12345',
                    'info': 'foo',
                    'type': 'temperature',
                    'plugin': 'plugin-1',
                    'tags': [
                        'default/foo:bar',
                    ],
                },
            ]

            resp = synse_app.test_client.get(
                '/v3/scan' + qparam,
                gather_request=False,
            )
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns=expected,
            tag_groups=[],
            force=False,
            sort='plugin,sortIndex,id',
        )

    @pytest.mark.parametrize(
        'qparam,expected', [
            ('?sort=', 'plugin,sortIndex,id'),
            ('?sort=plugin,sortIndex,id', 'plugin,sortIndex,id'),
            ('?sort=foo', 'foo'),
            ('?sort=test', 'test'),
            ('?sort=a,b,c,d', 'a,b,c,d'),
        ]
    )
    def test_param_sort_keys(self, synse_app, qparam, expected):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            mock_cmd.return_value = [
                {
                    'id': '12345',
                    'info': 'foo',
                    'type': 'temperature',
                    'plugin': 'plugin-1',
                    'tags': [
                        'default/foo:bar',
                    ],
                },
            ]

            resp = synse_app.test_client.get(
                '/v3/scan' + qparam,
                gather_request=False,
            )
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tag_groups=[],
            force=False,
            sort=expected,
        )

    @pytest.mark.parametrize(
        'qparam,expected', [
            ('?force=', False),
            ('?force=false', False),
            ('?force=FALSE', False),
            ('?force=False', False),
            ('?force=foo', False),
            ('?force=.', False),
            ('?force=tru', False),
            ('?force=trueeee', False),
            ('?force=true', True),
            ('?force=True', True),
            ('?force=TRUE', True),
            ('?force=TrUe', True),
            ('?force=False&force=True', False),
            ('?force=True&force=False', True),
        ]
    )
    def test_param_force(self, synse_app, qparam, expected):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            mock_cmd.return_value = [
                {
                    'id': '12345',
                    'info': 'foo',
                    'type': 'temperature',
                    'plugin': 'plugin-1',
                    'tags': [
                        'default/foo:bar',
                    ],
                },
            ]

            resp = synse_app.test_client.get(
                '/v3/scan' + qparam,
                gather_request=False,
            )
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tag_groups=[],
            force=expected,
            sort='plugin,sortIndex,id',
        )

    @pytest.mark.parametrize(
        'qparam,expected', [
            ('?tags=', []),
            ('?tags=a,b,c', [['a', 'b', 'c']]),
            ('?tags=a&tags=b&tags=c', [['a'], ['b'], ['c']]),
            ('?tags=default/foo', [['default/foo']]),
            ('?tags=default/foo:bar', [['default/foo:bar']]),
            ('?tags=foo:bar', [['foo:bar']]),
            ('?tags=foo:bar&tags=default/foo:baz&tags=vapor', [['foo:bar'], ['default/foo:baz'], ['vapor']]),  # noqa: E501
            ('?tags=default/foo,bar&tags=vapor/test', [['default/foo', 'bar'], ['vapor/test']]),
        ]
    )
    def test_param_tags(self, synse_app, qparam, expected):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            mock_cmd.return_value = [
                {
                    'id': '12345',
                    'info': 'foo',
                    'type': 'temperature',
                    'plugin': 'plugin-1',
                    'tags': [
                        'default/foo:bar',
                    ],
                },
            ]

            resp = synse_app.test_client.get(
                '/v3/scan' + qparam,
                gather_request=False,
            )
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tag_groups=expected,
            force=False,
            sort='plugin,sortIndex,id',
        )


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

    def test_ok(self, synse_app):
        with asynctest.patch('synse_server.cmd.tags') as mock_cmd:
            mock_cmd.return_value = [
                'foo:bar',
                'default/test',
                'vapor/unit:test',
            ]

            resp = synse_app.test_client.get('/v3/tags', gather_request=False)
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            [],
            with_id_tags=False,
        )

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
            [],
            with_id_tags=False
        )

    @pytest.mark.parametrize(
        'qparam,expected', [
            ('?ns=', []),
            ('?ns=default', ['default']),
            ('?ns=foo', ['foo']),
            ('?ns=one,two,three', ['one', 'two', 'three']),
            ('?ns=test&ns=vapor', ['test', 'vapor']),
            ('?ns=a,b&ns=c,d', ['a', 'b', 'c', 'd']),
        ]
    )
    def test_param_ns(self, synse_app, qparam, expected):
        with asynctest.patch('synse_server.cmd.tags') as mock_cmd:
            mock_cmd.return_value = [
                'foo:bar',
                'default/test',
                'vapor/unit:test',
            ]

            resp = synse_app.test_client.get(
                '/v3/tags' + qparam,
                gather_request=False,
            )
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            expected,
            with_id_tags=False,
        )

    @pytest.mark.parametrize(
        'qparam,expected', [
            ('?ids=', False),
            ('?ids=false', False),
            ('?ids=FALSE', False),
            ('?ids=False', False),
            ('?ids=foo', False),
            ('?ids=.', False),
            ('?ids=tru', False),
            ('?ids=trueeee', False),
            ('?ids=true', True),
            ('?ids=True', True),
            ('?ids=TRUE', True),
            ('?ids=TrUe', True),
            ('?ids=False&id=True', False),
            ('?ids=True&id=False', True),
        ]
    )
    def test_param_ids(self, synse_app, qparam, expected):
        with asynctest.patch('synse_server.cmd.tags') as mock_cmd:
            mock_cmd.return_value = [
                'foo:bar',
                'default/test',
                'vapor/unit:test',
            ]

            resp = synse_app.test_client.get(
                '/v3/tags' + qparam,
                gather_request=False,
            )
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            [],
            with_id_tags=expected,
        )


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

    def test_ok(self, synse_app):
        with asynctest.patch('synse_server.cmd.info') as mock_cmd:
            mock_cmd.return_value = {
                'id': '12345',
                'type': 'temperature',
                'plugin': '54321',
                'tags': [
                    'foo/bar',
                ],
            }

            resp = synse_app.test_client.get('/v3/info/123', gather_request=False)
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with('123')

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

    def test_not_found(self, synse_app):
        with asynctest.patch('synse_server.cmd.info') as mock_cmd:
            mock_cmd.side_effect = errors.NotFound('device not found')

            resp = synse_app.test_client.get('/v3/info/123', gather_request=False)
            assert resp.status == 404
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'device not found',
                'description': 'resource not found',
                'http_code': 404,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with('123')


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

    def test_ok(self, synse_app):
        with asynctest.patch('synse_server.cmd.read') as mock_cmd:
            mock_cmd.return_value = [
                {
                    'value': 1,
                    'type': 'temperature',
                },
            ]

            resp = synse_app.test_client.get('/v3/read', gather_request=False)
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tag_groups=[],
        )

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
            tag_groups=[],
        )

    def test_invalid_multiple_ns(self, synse_app):
        with asynctest.patch('synse_server.cmd.read') as mock_cmd:

            resp = synse_app.test_client.get('/v3/read?ns=ns-1&ns=ns-2', gather_request=False)
            assert resp.status == 400
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'invalid parameter: only one default namespace may be specified',
                'description': 'invalid user input',
                'http_code': 400,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_not_called()

    @pytest.mark.parametrize(
        'qparam,expected', [
            ('?tags=', []),
            ('?tags=a,b,c', [['a', 'b', 'c']]),
            ('?tags=a&tags=b&tags=c', [['a'], ['b'], ['c']]),
            ('?tags=default/foo', [['default/foo']]),
            ('?tags=default/foo:bar', [['default/foo:bar']]),
            ('?tags=foo:bar', [['foo:bar']]),
            ('?tags=foo:bar&tags=default/foo:baz&tags=vapor', [['foo:bar'], ['default/foo:baz'], ['vapor']]),  # noqa: E501
            ('?tags=default/foo,bar&tags=vapor/test', [['default/foo', 'bar'], ['vapor/test']]),
        ]
    )
    def test_param_tags(self, synse_app, qparam, expected):
        with asynctest.patch('synse_server.cmd.read') as mock_cmd:
            mock_cmd.return_value = [
                {
                    'value': 1,
                    'type': 'temperature',
                },
            ]

            resp = synse_app.test_client.get(
                '/v3/read' + qparam,
                gather_request=False,
            )
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tag_groups=expected,
        )

    @pytest.mark.parametrize(
        'qparam,expected', [
            ('?ns=', 'default'),
            ('?ns=default', 'default'),
            ('?ns=foo', 'foo'),
            ('?ns=test', 'test'),
            ('?ns=TEST', 'TEST'),
            ('?ns=t.e.s.t', 't.e.s.t'),
        ]
    )
    def test_param_ns(self, synse_app, qparam, expected):
        with asynctest.patch('synse_server.cmd.read') as mock_cmd:
            mock_cmd.return_value = [
                {
                    'value': 1,
                    'type': 'temperature',
                },
            ]

            resp = synse_app.test_client.get(
                '/v3/read' + qparam,
                gather_request=False,
            )
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns=expected,
            tag_groups=[],
        )


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

    def test_ok(self, synse_app):
        # Need to define a side-effect function for the test rather than utilizing
        # asynctest's implicit behavior for iterable side_effects because the function
        # we are mocking (cmd.read_cache) is an async generator, and the implicit
        # handling via asynctest does not appear to to handle that case well.
        async def mock_read_cache(*args, **kwargs):
            values = [
                {
                    'value': 1,
                    'type': 'temperature',
                },
                {
                    'value': 2,
                    'type': 'temperature',
                },
                {
                    'value': 3,
                    'type': 'temperature',
                },
            ]

            for v in values:
                yield v

        with asynctest.patch('synse_server.api.http.cmd.read_cache') as mock_cmd:
            mock_cmd.side_effect = mock_read_cache

            resp = synse_app.test_client.get('/v3/readcache', gather_request=False)
            assert resp.status == 200
            assert resp.headers['Transfer-Encoding'] == 'chunked'
            assert resp.headers['Content-Type'] == 'application/json; charset=utf-8'

            # The response is streamed, so we cannot simply load it (it will not be
            # a valid single JSON document), so we compare just the body.
            assert resp.body == b'{"value":1,"type":"temperature"}\n{"value":2,"type":"temperature"}\n{"value":3,"type":"temperature"}\n'  # noqa: E501

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with('', '')

    def test_error(self, synse_app):
        # Need to define a side-effect function for the test rather than utilizing
        # asynctest's implicit behavior for iterable side_effects because the function
        # we are mocking (cmd.read_cache) is an async generator, and the implicit
        # handling via asynctest does not appear to to handle that case well.
        async def mock_read_cache(*args, **kwargs):
            for i in range(3):
                yield {"foo": "bar"}
                raise ValueError('***********')

        with asynctest.patch('synse_server.cmd.read_cache') as mock_cmd:
            mock_cmd.side_effect = mock_read_cache

            resp = synse_app.test_client.get('/v3/readcache', gather_request=False)
            assert resp.status == 200
            assert resp.headers['Transfer-Encoding'] == 'chunked'
            assert resp.headers['Content-Type'] == 'application/json; charset=utf-8'

            # The response is streamed, so we cannot simply load it (it will not be
            # a valid single JSON document), so we compare just the body.
            assert resp.body == b'{"foo":"bar"}\n'

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with('', '')

    def test_invalid_multiple_start(self, synse_app):
        with asynctest.patch('synse_server.cmd.read_cache') as mock_cmd:

            resp = synse_app.test_client.get(
                '/v3/readcache?start=123&start=321',
                gather_request=False,
            )
            assert resp.status == 400
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'invalid parameter: only one cache start may be specified',
                'description': 'invalid user input',
                'http_code': 400,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_not_called()

    def test_invalid_multiple_end(self, synse_app):
        with asynctest.patch('synse_server.cmd.read_cache') as mock_cmd:
            mock_cmd.side_effect = errors.InvalidUsage('invalid: end')

            resp = synse_app.test_client.get('/v3/readcache?end=123&end=321', gather_request=False)
            assert resp.status == 400
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'invalid parameter: only one cache end may be specified',
                'description': 'invalid user input',
                'http_code': 400,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_not_called()

    @pytest.mark.parametrize(
        'qparam,expected', [
            ('?start=', ''),
            ('?start=foo', 'foo'),
            ('?start=2019-04-22T13:30:00Z', '2019-04-22T13:30:00Z'),
        ]
    )
    def test_param_start(self, synse_app, qparam, expected):
        # Need to define a side-effect function for the test rather than utilizing
        # asynctest's implicit behavior for iterable side_effects because the function
        # we are mocking (cmd.read_cache) is an async generator, and the implicit
        # handling via asynctest does not appear to to handle that case well.
        async def mock_read_cache(*args, **kwargs):
            values = [
                {
                    'value': 1,
                    'type': 'temperature',
                },
            ]

            for v in values:
                yield v

        with asynctest.patch('synse_server.cmd.read_cache') as mock_cmd:
            mock_cmd.side_effect = mock_read_cache

            resp = synse_app.test_client.get(
                '/v3/readcache' + qparam,
                gather_request=False,
            )
            assert resp.status == 200
            assert resp.headers['Transfer-Encoding'] == 'chunked'
            assert resp.headers['Content-Type'] == 'application/json; charset=utf-8'

            # The response is streamed, so we cannot simply load it (it will not be
            # a valid single JSON document), so we compare just the body.
            assert resp.body == b'{"value":1,"type":"temperature"}\n'

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(expected, '')

    @pytest.mark.parametrize(
        'qparam,expected', [
            ('?end=', ''),
            ('?end=foo', 'foo'),
            ('?end=2019-04-22T13:30:00Z', '2019-04-22T13:30:00Z'),
        ]
    )
    def test_param_end(self, synse_app, qparam, expected):
        # Need to define a side-effect function for the test rather than utilizing
        # asynctest's implicit behavior for iterable side_effects because the function
        # we are mocking (cmd.read_cache) is an async generator, and the implicit
        # handling via asynctest does not appear to to handle that case well.
        async def mock_read_cache(*args, **kwargs):
            values = [
                {
                    'value': 1,
                    'type': 'temperature',
                },
            ]

            for v in values:
                yield v

        with asynctest.patch('synse_server.cmd.read_cache') as mock_cmd:
            mock_cmd.side_effect = mock_read_cache

            resp = synse_app.test_client.get(
                '/v3/readcache' + qparam,
                gather_request=False,
            )
            assert resp.status == 200
            assert resp.headers['Transfer-Encoding'] == 'chunked'
            assert resp.headers['Content-Type'] == 'application/json; charset=utf-8'

            # The response is streamed, so we cannot simply load it (it will not be
            # a valid single JSON document), so we compare just the body.
            assert resp.body == b'{"value":1,"type":"temperature"}\n'

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with('', expected)


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

    def test_ok(self, synse_app):
        with asynctest.patch('synse_server.cmd.read_device') as mock_cmd:
            mock_cmd.return_value = [
                {
                    'value': 1,
                    'type': 'temperature',
                },
                {
                    'value': 2,
                    'type': 'temperature',
                },
            ]

            resp = synse_app.test_client.get('/v3/read/123', gather_request=False)
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with('123')

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

    def test_not_found(self, synse_app):
        with asynctest.patch('synse_server.cmd.read_device') as mock_cmd:
            mock_cmd.side_effect = errors.NotFound('device not found')

            resp = synse_app.test_client.get('/v3/read/123', gather_request=False)
            assert resp.status == 404
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'device not found',
                'description': 'resource not found',
                'http_code': 404,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with('123')

    def test_read_not_supported(self, synse_app):
        with asynctest.patch('synse_server.cmd.read_device') as mock_cmd:
            mock_cmd.side_effect = errors.UnsupportedAction('not supported')

            resp = synse_app.test_client.get('/v3/read/123', gather_request=False)
            assert resp.status == 405
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'not supported',
                'description': 'device action not supported',
                'http_code': 405,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with('123')


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

    def test_ok(self, synse_app):
        with asynctest.patch('synse_server.cmd.write_async') as mock_cmd:
            mock_cmd.return_value = [
                {
                    'id': 'txn-1',
                    'device': 'dev-1',
                },
                {
                    'id': 'txn-2',
                    'device': 'dev-1',
                },
            ]

            resp = synse_app.test_client.post(
                '/v3/write/123',
                data=ujson.dumps({'action': 'foo', 'data': 'bar'}),
                gather_request=False,
            )
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            device_id='123',
            payload=[{'action': 'foo', 'data': 'bar'}],
        )

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

    def test_invalid_json(self, synse_app):
        with asynctest.patch('synse_server.cmd.write_async') as mock_cmd:

            resp = synse_app.test_client.post(
                '/v3/write/123',
                data='invalid json data',
                gather_request=False,
            )
            assert resp.status == 400
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'invalid json: unable to parse POSTed body as JSON',
                'description': 'invalid user input',
                'http_code': 400,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_not_called()

    def test_invalid_json_missing_key(self, synse_app):
        with asynctest.patch('synse_server.cmd.write_async') as mock_cmd:

            resp = synse_app.test_client.post(
                '/v3/write/123',
                data=ujson.dumps({'data': 'bar'}),
                gather_request=False,
            )
            assert resp.status == 400
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'invalid json: key "action" is required in payload, but not found',
                'description': 'invalid user input',
                'http_code': 400,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_not_called()

    def test_not_found(self, synse_app):
        with asynctest.patch('synse_server.cmd.write_async') as mock_cmd:
            mock_cmd.side_effect = errors.NotFound('device not found')

            resp = synse_app.test_client.post(
                '/v3/write/123',
                data=ujson.dumps({'action': 'foo', 'data': 'bar'}),
                gather_request=False,
            )
            assert resp.status == 404
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'device not found',
                'description': 'resource not found',
                'http_code': 404,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            device_id='123',
            payload=[{'action': 'foo', 'data': 'bar'}],
        )

    def test_write_not_supported(self, synse_app):
        with asynctest.patch('synse_server.cmd.write_async') as mock_cmd:
            mock_cmd.side_effect = errors.UnsupportedAction('not supported')

            resp = synse_app.test_client.post(
                '/v3/write/123',
                data=ujson.dumps({'action': 'foo', 'data': 'bar'}),
                gather_request=False,
            )
            assert resp.status == 405
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'not supported',
                'description': 'device action not supported',
                'http_code': 405,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            device_id='123',
            payload=[{'action': 'foo', 'data': 'bar'}],
        )


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

    def test_ok(self, synse_app):
        with asynctest.patch('synse_server.cmd.write_sync') as mock_cmd:
            mock_cmd.return_value = [
                {
                    'id': 'txn-1',
                    'device': 'dev-1',
                },
                {
                    'id': 'txn-2',
                    'device': 'dev-1',
                },
            ]

            resp = synse_app.test_client.post(
                '/v3/write/wait/123',
                data=ujson.dumps({'action': 'foo', 'data': 'bar'}),
                gather_request=False,
            )
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            device_id='123',
            payload=[{'action': 'foo', 'data': 'bar'}],
        )

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

    def test_invalid_json(self, synse_app):
        with asynctest.patch('synse_server.cmd.write_sync') as mock_cmd:

            resp = synse_app.test_client.post(
                '/v3/write/wait/123',
                data='invalid json data',
                gather_request=False,
            )
            assert resp.status == 400
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'invalid json: unable to parse POSTed body as JSON',
                'description': 'invalid user input',
                'http_code': 400,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_not_called()

    def test_invalid_json_missing_key(self, synse_app):
        with asynctest.patch('synse_server.cmd.write_sync') as mock_cmd:

            resp = synse_app.test_client.post(
                '/v3/write/wait/123',
                data=ujson.dumps({'data': 'bar'}),
                gather_request=False,
            )
            assert resp.status == 400
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'invalid json: key "action" is required in payload, but not found',
                'description': 'invalid user input',
                'http_code': 400,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_not_called()

    def test_not_found(self, synse_app):
        with asynctest.patch('synse_server.cmd.write_sync') as mock_cmd:
            mock_cmd.side_effect = errors.NotFound('device not found')

            resp = synse_app.test_client.post(
                '/v3/write/wait/123',
                data=ujson.dumps({'action': 'foo', 'data': 'bar'}),
                gather_request=False,
            )
            assert resp.status == 404
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'device not found',
                'description': 'resource not found',
                'http_code': 404,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            device_id='123',
            payload=[{'action': 'foo', 'data': 'bar'}],
        )

    def test_write_not_supported(self, synse_app):
        with asynctest.patch('synse_server.cmd.write_sync') as mock_cmd:
            mock_cmd.side_effect = errors.UnsupportedAction('not supported')

            resp = synse_app.test_client.post(
                '/v3/write/wait/123',
                data=ujson.dumps({'action': 'foo', 'data': 'bar'}),
                gather_request=False,
            )
            assert resp.status == 405
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'not supported',
                'description': 'device action not supported',
                'http_code': 405,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            device_id='123',
            payload=[{'action': 'foo', 'data': 'bar'}],
        )


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

    def test_ok(self, synse_app):
        with asynctest.patch('synse_server.cmd.transactions') as mock_cmd:
            mock_cmd.return_value = [
                'txn-1',
                'txn-2',
                'txn-3',
                'txn-4',
                'txn-5',
            ]

            resp = synse_app.test_client.get('/v3/transaction', gather_request=False)
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()

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

    def test_ok(self, synse_app):
        with asynctest.patch('synse_server.cmd.transaction') as mock_cmd:
            mock_cmd.return_value = {
                'id': 'txn-1',
                'device': '123456',
                'created': '2019-04-22T13:30:00Z',
                'updated': '2019-04-22T13:30:00Z',
                'message': '',
                'timeout': '5s',
            }

            resp = synse_app.test_client.get('/v3/transaction/123', gather_request=False)
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with('123')

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

    def test_not_found(self, synse_app):
        with asynctest.patch('synse_server.cmd.transaction') as mock_cmd:
            mock_cmd.side_effect = errors.NotFound('transaction not found')

            resp = synse_app.test_client.get('/v3/transaction/123', gather_request=False)
            assert resp.status == 404
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'transaction not found',
                'description': 'resource not found',
                'http_code': 404,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with('123')


@pytest.mark.usefixtures('patch_utils_rfc3339now')
class TestV3Device:
    """Test for the Synse v3 API 'device' route."""

    #
    # Tests for /device
    #
    # Note: Since the /device route is just an alias for the /scan route
    # to make the API more consistent/RESTful, these tests are effectively
    # the same as the scan tests.
    #

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
    def test_enumerate_methods_not_allowed(self, synse_app, method):
        fn = getattr(synse_app.test_client, method)
        response = fn('/v3/device', gather_request=False)
        assert response.status == 405

    def test_enumerate_ok(self, synse_app):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            mock_cmd.return_value = [
                {
                    'id': '12345',
                    'info': 'foo',
                    'type': 'temperature',
                    'plugin': 'plugin-1',
                    'tags': [
                        'default/foo:bar',
                    ],
                },
                {
                    'id': '54321',
                    'info': 'bar',
                    'type': 'temperature',
                    'plugin': 'plugin-2',
                    'tags': [
                        'default/foo:bar',
                    ],
                },
            ]

            resp = synse_app.test_client.get('/v3/device', gather_request=False)
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tag_groups=[],
            force=False,
            sort='plugin,sortIndex,id',
        )

    def test_enumerate_error(self, synse_app):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            mock_cmd.side_effect = ValueError('***********')

            resp = synse_app.test_client.get('/v3/device', gather_request=False)
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
            tag_groups=[],
            force=False,
            sort='plugin,sortIndex,id',
        )

    def test_enumerate_invalid_multiple_ns(self, synse_app):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            resp = synse_app.test_client.get('/v3/device?ns=ns-1&ns=ns-2', gather_request=False)
            assert resp.status == 400
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'invalid parameter: only one namespace may be specified',
                'description': 'invalid user input',
                'http_code': 400,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_not_called()

    def test_enumerate_invalid_multiple_sort(self, synse_app):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            resp = synse_app.test_client.get('/v3/device?sort=id&sort=type', gather_request=False)
            assert resp.status == 400
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'invalid parameter: only one sort key may be specified',
                'description': 'invalid user input',
                'http_code': 400,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_not_called()

    @pytest.mark.parametrize(
        'qparam,expected', [
            ('?ns=', 'default'),
            ('?ns=default', 'default'),
            ('?ns=foo', 'foo'),
            ('?ns=test', 'test'),
            ('?ns=TEST', 'TEST'),
            ('?ns=t.e.s.t', 't.e.s.t'),
        ]
    )
    def test_enumerate_param_ns(self, synse_app, qparam, expected):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            mock_cmd.return_value = [
                {
                    'id': '12345',
                    'info': 'foo',
                    'type': 'temperature',
                    'plugin': 'plugin-1',
                    'tags': [
                        'default/foo:bar',
                    ],
                },
            ]

            resp = synse_app.test_client.get(
                '/v3/device' + qparam,
                gather_request=False,
            )
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns=expected,
            tag_groups=[],
            force=False,
            sort='plugin,sortIndex,id',
        )

    @pytest.mark.parametrize(
        'qparam,expected', [
            ('?sort=', 'plugin,sortIndex,id'),
            ('?sort=plugin,sortIndex,id', 'plugin,sortIndex,id'),
            ('?sort=foo', 'foo'),
            ('?sort=test', 'test'),
            ('?sort=a,b,c,d', 'a,b,c,d'),
        ]
    )
    def test_enumerate_param_sort_keys(self, synse_app, qparam, expected):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            mock_cmd.return_value = [
                {
                    'id': '12345',
                    'info': 'foo',
                    'type': 'temperature',
                    'plugin': 'plugin-1',
                    'tags': [
                        'default/foo:bar',
                    ],
                },
            ]

            resp = synse_app.test_client.get(
                '/v3/device' + qparam,
                gather_request=False,
            )
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tag_groups=[],
            force=False,
            sort=expected,
        )

    @pytest.mark.parametrize(
        'qparam,expected', [
            ('?force=', False),
            ('?force=false', False),
            ('?force=FALSE', False),
            ('?force=False', False),
            ('?force=foo', False),
            ('?force=.', False),
            ('?force=tru', False),
            ('?force=trueeee', False),
            ('?force=true', True),
            ('?force=True', True),
            ('?force=TRUE', True),
            ('?force=TrUe', True),
            ('?force=False&force=True', False),
            ('?force=True&force=False', True),
        ]
    )
    def test_enumerate_param_force(self, synse_app, qparam, expected):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            mock_cmd.return_value = [
                {
                    'id': '12345',
                    'info': 'foo',
                    'type': 'temperature',
                    'plugin': 'plugin-1',
                    'tags': [
                        'default/foo:bar',
                    ],
                },
            ]

            resp = synse_app.test_client.get(
                '/v3/device' + qparam,
                gather_request=False,
            )
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tag_groups=[],
            force=expected,
            sort='plugin,sortIndex,id',
        )

    @pytest.mark.parametrize(
        'qparam,expected', [
            ('?tags=', []),
            ('?tags=a,b,c', [['a', 'b', 'c']]),
            ('?tags=a&tags=b&tags=c', [['a'], ['b'], ['c']]),
            ('?tags=default/foo', [['default/foo']]),
            ('?tags=default/foo:bar', [['default/foo:bar']]),
            ('?tags=foo:bar', [['foo:bar']]),
            ('?tags=foo:bar&tags=default/foo:baz&tags=vapor', [['foo:bar'], ['default/foo:baz'], ['vapor']]),  # noqa: E501
            ('?tags=default/foo,bar&tags=vapor/test', [['default/foo', 'bar'], ['vapor/test']]),
        ]
    )
    def test_enumerate_param_tags(self, synse_app, qparam, expected):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            mock_cmd.return_value = [
                {
                    'id': '12345',
                    'info': 'foo',
                    'type': 'temperature',
                    'plugin': 'plugin-1',
                    'tags': [
                        'default/foo:bar',
                    ],
                },
            ]

            resp = synse_app.test_client.get(
                '/v3/device' + qparam,
                gather_request=False,
            )
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tag_groups=expected,
            force=False,
            sort='plugin,sortIndex,id',
        )

    #
    # Tests for /device/<id>
    #

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

    def test_read_ok(self, synse_app):
        with asynctest.patch('synse_server.cmd.read_device') as mock_cmd:
            mock_cmd.return_value = [
                {
                    'value': 1,
                    'type': 'temperature',
                },
                {
                    'value': 2,
                    'type': 'temperature',
                },
            ]

            resp = synse_app.test_client.get('/v3/device/123', gather_request=False)
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with('123')

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

    def test_read_not_found(self, synse_app):
        with asynctest.patch('synse_server.cmd.read_device') as mock_cmd:
            mock_cmd.side_effect = errors.NotFound('device not found')

            resp = synse_app.test_client.get('/v3/read/123', gather_request=False)
            assert resp.status == 404
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'device not found',
                'description': 'resource not found',
                'http_code': 404,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with('123')

    def test_read_not_supported(self, synse_app):
        with asynctest.patch('synse_server.cmd.read_device') as mock_cmd:
            mock_cmd.side_effect = errors.UnsupportedAction('not supported')

            resp = synse_app.test_client.get('/v3/read/123', gather_request=False)
            assert resp.status == 405
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'not supported',
                'description': 'device action not supported',
                'http_code': 405,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with('123')

    def test_write_ok(self, synse_app):
        with asynctest.patch('synse_server.cmd.write_sync') as mock_cmd:
            mock_cmd.return_value = [
                {
                    'id': 'txn-1',
                    'device': 'dev-1',
                },
                {
                    'id': 'txn-2',
                    'device': 'dev-1',
                },
            ]

            resp = synse_app.test_client.post(
                '/v3/device/123',
                data=ujson.dumps({'action': 'foo', 'data': 'bar'}),
                gather_request=False,
            )
            assert resp.status == 200
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == mock_cmd.return_value

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            device_id='123',
            payload=[{'action': 'foo', 'data': 'bar'}],
        )

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

    def test_write_invalid_json(self, synse_app):
        with asynctest.patch('synse_server.cmd.write_sync') as mock_cmd:

            resp = synse_app.test_client.post(
                '/v3/write/wait/123',
                data='invalid json data',
                gather_request=False,
            )
            assert resp.status == 400
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'invalid json: unable to parse POSTed body as JSON',
                'description': 'invalid user input',
                'http_code': 400,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_not_called()

    def test_write_invalid_json_missing_key(self, synse_app):
        with asynctest.patch('synse_server.cmd.write_sync') as mock_cmd:

            resp = synse_app.test_client.post(
                '/v3/write/wait/123',
                data=ujson.dumps({'data': 'bar'}),
                gather_request=False,
            )
            assert resp.status == 400
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'invalid json: key "action" is required in payload, but not found',
                'description': 'invalid user input',
                'http_code': 400,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_not_called()

    def test_write_not_found(self, synse_app):
        with asynctest.patch('synse_server.cmd.write_sync') as mock_cmd:
            mock_cmd.side_effect = errors.NotFound('device not found')

            resp = synse_app.test_client.post(
                '/v3/write/wait/123',
                data=ujson.dumps({'action': 'foo', 'data': 'bar'}),
                gather_request=False,
            )
            assert resp.status == 404
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'device not found',
                'description': 'resource not found',
                'http_code': 404,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            device_id='123',
            payload=[{'action': 'foo', 'data': 'bar'}],
        )

    def test_write_not_supported(self, synse_app):
        with asynctest.patch('synse_server.cmd.write_sync') as mock_cmd:
            mock_cmd.side_effect = errors.UnsupportedAction('not supported')

            resp = synse_app.test_client.post(
                '/v3/write/wait/123',
                data=ujson.dumps({'action': 'foo', 'data': 'bar'}),
                gather_request=False,
            )
            assert resp.status == 405
            assert resp.headers['Content-Type'] == 'application/json'

            body = ujson.loads(resp.body)
            assert body == {
                'context': 'not supported',
                'description': 'device action not supported',
                'http_code': 405,
                'timestamp': '2019-04-22T13:30:00Z',
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            device_id='123',
            payload=[{'action': 'foo', 'data': 'bar'}],
        )
