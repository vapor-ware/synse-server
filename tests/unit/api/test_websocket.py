
import json

import asynctest
import pytest
import websockets

from synse_server import errors
from synse_server.api import websocket


def make_payload(data, id=None, event=None):
    """Test utility to create a websocket payload, with some defaults."""
    return websocket.Payload(json.dumps(dict(
        id=id or 'testing',
        event=event or 'testing',
        data=data,
    )))


@pytest.mark.usefixtures('patch_utils_rfc3339now')
def test_error_no_exception():
    resp = websocket.error()

    assert resp == {
        'id': -1,
        'event': 'response/error',
        'data': {
            'description': 'An unexpected error occurred.',
            'timestamp': '2019-04-22T13:30:00Z',
        }
    }


@pytest.mark.usefixtures('patch_utils_rfc3339now')
def test_error_synse_error():
    resp = websocket.error(
        msg_id=1,
        ex=errors.InvalidUsage('invalid'),
    )

    assert resp == {
        'id': 1,
        'event': 'response/error',
        'data': {
            'http_code': 400,
            'description': 'invalid user input',
            'timestamp': '2019-04-22T13:30:00Z',
            'context': 'invalid',
        }
    }


@pytest.mark.usefixtures('patch_utils_rfc3339now')
def test_error_other_error():
    resp = websocket.error(
        msg_id=3,
        message='test message',
        ex=ValueError('uh oh'),
    )

    assert resp == {
        'id': 3,
        'event': 'response/error',
        'data': {
            'http_code': 500,
            'description': 'test message',
            'timestamp': '2019-04-22T13:30:00Z',
            'context': 'uh oh',
        }
    }


class TestPayload:
    """Tests for the WebSocket Payload class."""

    def test_init_ok(self):
        data = '{"id": 1, "event": "test", "data": {"foo": "bar"}}'

        payload = websocket.Payload(data)

        assert isinstance(payload, websocket.Payload)
        assert payload.id == 1
        assert payload.event == 'test'
        assert payload.data == {'foo': 'bar'}

    def test_init_json_error(self):
        data = '{{"}'

        with pytest.raises(Exception):
            websocket.Payload(data)

    @pytest.mark.parametrize('data', [
        '{"event": "test", "data": {"foo": "bar"}}',
        '{"id": 1, "data": {"foo": "bar"}}'
    ])
    def test_init_missing_required(self, data):
        with pytest.raises(ValueError):
            websocket.Payload(data)

    def test_init_missing_optional(self):
        data = '{"id": 1, "event": "test"}'

        payload = websocket.Payload(data)

        assert isinstance(payload, websocket.Payload)
        assert payload.id == 1
        assert payload.event == 'test'
        assert payload.data == {}


class TestMessageHandler:
    """Tests for the WebSocket MessageHandler class."""

    @pytest.mark.asyncio
    async def test_response(self):
        with asynctest.patch('synse_server.api.websocket.MessageHandler.handle_request_status') as mock_handler:  # noqa: E501

            p = websocket.Payload(json.dumps(dict(
                id=2,
                event='request/status',
                data={},
            )))
            m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
            await m.dispatch(p)

        mock_handler.assert_called_once()

    @pytest.mark.asyncio
    @pytest.mark.usefixtures('patch_utils_rfc3339now')
    async def test_response_no_handler(self):
        with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:

            p = websocket.Payload(json.dumps(dict(
                id=3,
                event='foo/bar',
                data={},
            )))
            m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
            await m.dispatch(p)

        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 3,
            'event': 'response/error',
            'data': {
                'description': 'unsupported event type: foo/bar',
                'timestamp': '2019-04-22T13:30:00Z',
            }
        }))

    @pytest.mark.asyncio
    @pytest.mark.usefixtures('patch_utils_rfc3339now')
    async def test_response_error(self):
        with asynctest.patch('synse_server.api.websocket.MessageHandler.handle_request_status') as mock_handler:  # noqa: E501
            mock_handler.side_effect = ValueError('test error')
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:

                p = websocket.Payload(json.dumps(dict(
                    id=4,
                    event='request/status',
                    data={},
                )))
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.dispatch(p)

            mock_send.assert_called_once()
            mock_send.assert_called_with(json.dumps({
                'id': 4,
                'event': 'response/error',
                'data': {
                    'http_code': 500,
                    'description': 'An unexpected error occurred.',
                    'timestamp': '2019-04-22T13:30:00Z',
                    'context': 'test error',
                }
            }))

    @pytest.mark.asyncio
    async def test_request_status(self):
        with asynctest.patch('synse_server.cmd.test') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = {
                    'status': 'ok',
                    'timestamp': '2019-04-22T13:30:00Z',
                }

                p = make_payload(data={})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_status(p)

        mock_cmd.assert_called_once()
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/status',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_version(self):
        with asynctest.patch('synse_server.cmd.version') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = {
                    'version': '3.0.0',
                    'api_version': 'v3',
                }

                p = make_payload(data={})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_version(p)

        mock_cmd.assert_called_once()
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/version',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_config(self):
        with asynctest.patch('synse_server.cmd.config') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = {
                    'key': 'value',
                }

                p = make_payload(data={})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_config(p)

        mock_cmd.assert_called_once()
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/config',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_plugins(self):
        with asynctest.patch('synse_server.cmd.plugins') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = [{
                    'key': 'value',
                }]

                p = make_payload(data={})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_plugins(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with()
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/plugin_summary',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_plugin(self):
        with asynctest.patch('synse_server.cmd.plugin') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = [{
                    'key': 'value',
                }]

                p = make_payload(data={'plugin': '123'})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_plugin(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with('123')
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/plugin_info',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_plugin_invalid_usage(self):
        with asynctest.patch('synse_server.cmd.plugin') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = [{
                    'key': 'value',
                }]

                p = make_payload(data={})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                with pytest.raises(errors.InvalidUsage):
                    await m.handle_request_plugin(p)

        mock_cmd.assert_not_called()
        mock_send.assert_not_called()

    @pytest.mark.asyncio
    async def test_request_plugin_health(self):
        with asynctest.patch('synse_server.cmd.plugin_health') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = {
                    'key': 'value',
                }

                p = make_payload(data={})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_plugin_health(p)

        mock_cmd.assert_called_once()
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/plugin_health',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_scan_no_data(self):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = [{
                    'key': 'value',
                }]

                p = make_payload(data={})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_scan(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tag_groups=[],
            sort='plugin,sortIndex,id',
            force=False,
        )
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/device_summary',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_scan_data_force(self):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = [{
                    'key': 'value',
                }]

                p = make_payload(data={'force': True})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_scan(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tag_groups=[],
            sort='plugin,sortIndex,id',
            force=True,
        )
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/device_summary',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_scan_data_namespace(self):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = [{
                    'key': 'value',
                }]

                p = make_payload(data={'ns': 'vapor'})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_scan(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='vapor',
            tag_groups=[],
            sort='plugin,sortIndex,id',
            force=False,
        )
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/device_summary',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_scan_data_tags_one_group(self):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = [{
                    'key': 'value',
                }]

                p = make_payload(data={'tags': [['ns/ann:lab', 'foo']]})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_scan(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tag_groups=[['ns/ann:lab', 'foo']],
            sort='plugin,sortIndex,id',
            force=False,
        )
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/device_summary',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_scan_data_tags_implicit_group(self):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = [{
                    'key': 'value',
                }]

                p = make_payload(data={'tags': ['ns/ann:lab', 'foo']})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_scan(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tag_groups=[['ns/ann:lab', 'foo']],
            sort='plugin,sortIndex,id',
            force=False,
        )
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/device_summary',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_scan_data_tags_multiple_groups(self):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = [{
                    'key': 'value',
                }]

                p = make_payload(data={'tags': [['ns/ann:lab', 'foo'], ['bar']]})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_scan(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tag_groups=[['ns/ann:lab', 'foo'], ['bar']],
            sort='plugin,sortIndex,id',
            force=False,
        )
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/device_summary',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_tags_no_data(self):
        with asynctest.patch('synse_server.cmd.tags') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = [
                    'foo/bar',
                    'vapor:io',
                ]

                p = make_payload(data={})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_tags(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            with_id_tags=False,
        )
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/tags',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_tags_data_ns(self):
        with asynctest.patch('synse_server.cmd.tags') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = [
                    'foo/bar',
                    'vapor:io',
                ]

                p = make_payload(data={'ns': ['a', 'b', 'c']})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_tags(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            'a', 'b', 'c',
            with_id_tags=False,
        )
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/tags',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_tags_data_ids(self):
        with asynctest.patch('synse_server.cmd.tags') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = [
                    'foo/bar',
                    'vapor:io',
                ]

                p = make_payload(data={'ids': True})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_tags(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            with_id_tags=True,
        )
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/tags',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_info(self):
        with asynctest.patch('synse_server.cmd.info') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = {
                    'key': 'value',
                }

                p = make_payload(data={'device': '123'})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_info(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            device_id='123',
        )
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/device_info',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_info_error(self):
        with asynctest.patch('synse_server.cmd.info') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = {
                    'key': 'value',
                }

                p = make_payload(data={})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                with pytest.raises(errors.InvalidUsage):
                    await m.handle_request_info(p)

        mock_cmd.assert_not_called()
        mock_send.assert_not_called()

    @pytest.mark.asyncio
    async def test_request_read_no_data(self):
        with asynctest.patch('synse_server.cmd.read') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = [{
                    'key': 'value',
                }]

                p = make_payload(data={})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_read(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tag_groups=[],
        )
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/reading',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_read_data_ns(self):
        with asynctest.patch('synse_server.cmd.read') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = [{
                    'key': 'value',
                }]

                p = make_payload(data={'ns': 'foo'})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_read(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='foo',
            tag_groups=[],
        )
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/reading',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_read_data_tags_one_group(self):
        with asynctest.patch('synse_server.cmd.read') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = [{
                    'key': 'value',
                }]

                p = make_payload(data={'tags': [['foo', 'bar']]})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_read(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tag_groups=[['foo', 'bar']],
        )
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/reading',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_read_data_tags_implicit_group(self):
        with asynctest.patch('synse_server.cmd.read') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = [{
                    'key': 'value',
                }]

                p = make_payload(data={'tags': ['foo', 'bar']})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_read(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tag_groups=[['foo', 'bar']],
        )
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/reading',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_read_data_tags_multiple_groups(self):
        with asynctest.patch('synse_server.cmd.read') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = [{
                    'key': 'value',
                }]

                p = make_payload(data={'tags': [['foo', 'bar'], ['baz']]})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_read(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tag_groups=[['foo', 'bar'], ['baz']],
        )
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/reading',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_read_device(self):
        with asynctest.patch('synse_server.cmd.read_device') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = {
                    'key': 'value',
                }

                p = make_payload(data={'device': '123'})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_read_device(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            device_id='123',
        )
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/reading',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_read_device_error(self):
        with asynctest.patch('synse_server.cmd.read_device') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = {
                    'key': 'value',
                }

                p = make_payload(data={})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                with pytest.raises(errors.InvalidUsage):
                    await m.handle_request_read_device(p)

        mock_cmd.assert_not_called()
        mock_send.assert_not_called()

    @pytest.mark.asyncio
    async def test_request_read_cache_no_data(self):
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

        with asynctest.patch('synse_server.cmd.read_cache') as mock_cmd:
            mock_cmd.side_effect = mock_read_cache
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:

                p = make_payload(data={})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_read_cache(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            start=None,
            end=None,
        )
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/reading',
            'data': [
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
            ],
        }))

    @pytest.mark.asyncio
    async def test_request_read_cache_data_start(self):
        # Need to define a side-effect function for the test rather than utilizing
        # asynctest's implicit behavior for iterable side_effects because the function
        # we are mocking (cmd.read_cache) is an async generator, and the implicit
        # handling via asynctest does not appear to to handle that case well.
        async def mock_read_cache(*args, **kwargs):
            values = [
                {
                    'value': 1,
                    'type': 'temperature',
                }
            ]

            for v in values:
                yield v

        with asynctest.patch('synse_server.cmd.read_cache') as mock_cmd:
            mock_cmd.side_effect = mock_read_cache
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:

                p = make_payload(data={'start': 'now'})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_read_cache(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            start='now',
            end=None,
        )
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/reading',
            'data': [
                {
                    'value': 1,
                    'type': 'temperature',
                }
            ],
        }))

    @pytest.mark.asyncio
    async def test_request_read_cache_data_end(self):
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
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:

                p = make_payload(data={'end': 'now'})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_read_cache(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            start=None,
            end='now',
        )
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/reading',
            'data': [
                {
                    'value': 1,
                    'type': 'temperature',
                },
            ],
        }))

    @pytest.mark.asyncio
    async def test_request_write_async(self):
        with asynctest.patch('synse_server.cmd.write_async') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = {
                    'key': 'value',
                }

                p = make_payload(data={'device': '123', 'payload': {'action': 'foo'}})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_write_async(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            device_id='123',
            payload={'action': 'foo'}
        )
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/transaction_info',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_write_async_error_id(self):
        with asynctest.patch('synse_server.cmd.write_async') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = {
                    'key': 'value',
                }

                p = make_payload(data={'payload': {'action': 'foo'}})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                with pytest.raises(errors.InvalidUsage):
                    await m.handle_request_write_async(p)

        mock_cmd.assert_not_called()
        mock_send.assert_not_called()

    @pytest.mark.asyncio
    async def test_request_write_async_error_payload(self):
        with asynctest.patch('synse_server.cmd.write_async') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = {
                    'key': 'value',
                }

                p = make_payload(data={'device': '123'})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                with pytest.raises(errors.InvalidUsage):
                    await m.handle_request_write_async(p)

        mock_cmd.assert_not_called()
        mock_send.assert_not_called()

    @pytest.mark.asyncio
    async def test_request_write_sync(self):
        with asynctest.patch('synse_server.cmd.write_sync') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = {
                    'key': 'value',
                }

                p = make_payload(data={'device': '123', 'payload': {'action': 'foo'}})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_write_sync(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            device_id='123',
            payload={'action': 'foo'}
        )
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/transaction_status',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_write_sync_error_id(self):
        with asynctest.patch('synse_server.cmd.write_sync') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = {
                    'key': 'value',
                }

                p = make_payload(data={'payload': {'action': 'foo'}})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                with pytest.raises(errors.InvalidUsage):
                    await m.handle_request_write_sync(p)

        mock_cmd.assert_not_called()
        mock_send.assert_not_called()

    @pytest.mark.asyncio
    async def test_request_write_sync_error_payload(self):
        with asynctest.patch('synse_server.cmd.write_sync') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = {
                    'key': 'value',
                }

                p = make_payload(data={'device': '123'})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                with pytest.raises(errors.InvalidUsage):
                    await m.handle_request_write_sync(p)

        mock_cmd.assert_not_called()
        mock_send.assert_not_called()

    @pytest.mark.asyncio
    async def test_request_transactions(self):
        with asynctest.patch('synse_server.cmd.transactions') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = [{
                    'key': 'value',
                }]

                p = make_payload(data={})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_transactions(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with()
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/transaction_list',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_transaction(self):
        with asynctest.patch('synse_server.cmd.transaction') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = [{
                    'key': 'value',
                }]

                p = make_payload(data={'transaction': 'foo'})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                await m.handle_request_transaction(p)

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with('foo')
        mock_send.assert_called_once()
        mock_send.assert_called_with(json.dumps({
            'id': 'testing',
            'event': 'response/transaction_status',
            'data': mock_cmd.return_value,
        }))

    @pytest.mark.asyncio
    async def test_request_transaction_invalid_usage(self):
        with asynctest.patch('synse_server.cmd.transaction') as mock_cmd:
            with asynctest.patch('websockets.WebSocketCommonProtocol.send') as mock_send:
                mock_cmd.return_value = [{
                    'key': 'value',
                }]

                p = make_payload(data={})
                m = websocket.MessageHandler(websockets.WebSocketCommonProtocol())
                with pytest.raises(errors.InvalidUsage):
                    await m.handle_request_transaction(p)

        mock_cmd.assert_not_called()
        mock_send.assert_not_called()
