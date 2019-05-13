
import json

import asynctest
import pytest

from synse_server import errors
from synse_server.api import websocket


class TestMessage:
    """Tests for the WebSocket Message handler class."""

    def test_from_json(self):
        pass

    def test_from_json_error(self):
        pass

    @pytest.mark.asyncio
    async def test_response(self):
        pass

    @pytest.mark.asyncio
    async def test_response_no_handler(self):
        pass

    @pytest.mark.asyncio
    async def test_response_error(self):
        pass

    @pytest.mark.asyncio
    async def test_request_status(self):
        with asynctest.patch('synse_server.cmd.test') as mock_cmd:
            mock_cmd.return_value = {
                'status': 'ok',
                'timestamp': '2019-04-22T13:30:00Z',
            }

            m = websocket.Message(id='testing', event='testing', data={})
            resp = await m.handle_request_status()

            assert resp == {
                'id': 'testing',
                'event': 'response/status',
                'data': mock_cmd.return_value,
            }

        mock_cmd.assert_called_once()

    @pytest.mark.asyncio
    async def test_request_version(self):
        with asynctest.patch('synse_server.cmd.version') as mock_cmd:
            mock_cmd.return_value = {
                'version': '3.0.0',
                'api_version': 'v3',
            }

            m = websocket.Message(id='testing', event='testing', data={})
            resp = await m.handle_request_version()

            assert resp == {
                'id': 'testing',
                'event': 'response/version',
                'data': mock_cmd.return_value,
            }

        mock_cmd.assert_called_once()

    @pytest.mark.asyncio
    async def test_request_config(self):
        with asynctest.patch('synse_server.cmd.config') as mock_cmd:
            mock_cmd.return_value = {
                'key': 'value',
            }

            m = websocket.Message(id='testing', event='testing', data={})
            resp = await m.handle_request_config()

            assert resp == {
                'id': 'testing',
                'event': 'response/config',
                'data': mock_cmd.return_value,
            }

        mock_cmd.assert_called_once()

    @pytest.mark.asyncio
    async def test_request_plugin_no_data(self):
        with asynctest.patch('synse_server.cmd.plugins') as mock_cmd:
            mock_cmd.return_value = [{
                'key': 'value',
            }]

            m = websocket.Message(id='testing', event='testing', data={})
            resp = await m.handle_request_plugin()

            assert resp == {
                'id': 'testing',
                'event': 'response/plugin',
                'data': mock_cmd.return_value,
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with()

    @pytest.mark.asyncio
    async def test_request_plugin_with_data(self):
        with asynctest.patch('synse_server.cmd.plugin') as mock_cmd:
            mock_cmd.return_value = [{
                'key': 'value',
            }]

            m = websocket.Message(id='testing', event='testing', data={'plugin': '123'})
            resp = await m.handle_request_plugin()

            assert resp == {
                'id': 'testing',
                'event': 'response/plugin',
                'data': mock_cmd.return_value,
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with('123')

    @pytest.mark.asyncio
    async def test_request_plugin_health(self):
        with asynctest.patch('synse_server.cmd.plugin_health') as mock_cmd:
            mock_cmd.return_value = {
                'key': 'value',
            }

            m = websocket.Message(id='testing', event='testing', data={})
            resp = await m.handle_request_plugin_health()

            assert resp == {
                'id': 'testing',
                'event': 'response/plugin_health',
                'data': mock_cmd.return_value,
            }

        mock_cmd.assert_called_once()

    @pytest.mark.asyncio
    async def test_request_scan_no_data(self):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            mock_cmd.return_value = [{
                'key': 'value',
            }]

            m = websocket.Message(id='testing', event='testing', data={})
            resp = await m.handle_request_scan()

            assert resp == {
                'id': 'testing',
                'event': 'response/scan',
                'data': mock_cmd.return_value,
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tags=[],
            sort='plugin,sortIndex,id',
            force=False,
        )

    @pytest.mark.asyncio
    async def test_request_scan_data_force(self):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            mock_cmd.return_value = [{
                'key': 'value',
            }]

            m = websocket.Message(id='testing', event='testing', data={'force': True})
            resp = await m.handle_request_scan()

            assert resp == {
                'id': 'testing',
                'event': 'response/scan',
                'data': mock_cmd.return_value,
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tags=[],
            sort='plugin,sortIndex,id',
            force=True,
        )

    @pytest.mark.asyncio
    async def test_request_scan_data_namespace(self):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            mock_cmd.return_value = [{
                'key': 'value',
            }]

            m = websocket.Message(id='testing', event='testing', data={'ns': 'vapor'})
            resp = await m.handle_request_scan()

            assert resp == {
                'id': 'testing',
                'event': 'response/scan',
                'data': mock_cmd.return_value,
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='vapor',
            tags=[],
            sort='plugin,sortIndex,id',
            force=False,
        )

    @pytest.mark.asyncio
    async def test_request_scan_data_tags(self):
        with asynctest.patch('synse_server.cmd.scan') as mock_cmd:
            mock_cmd.return_value = [{
                'key': 'value',
            }]

            m = websocket.Message(id='testing', event='testing', data={'tags': ['ns/ann:lab', 'foo']})
            resp = await m.handle_request_scan()

            assert resp == {
                'id': 'testing',
                'event': 'response/scan',
                'data': mock_cmd.return_value,
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tags=['ns/ann:lab', 'foo'],
            sort='plugin,sortIndex,id',
            force=False,
        )

    @pytest.mark.asyncio
    async def test_request_tags_no_data(self):
        with asynctest.patch('synse_server.cmd.tags') as mock_cmd:
            mock_cmd.return_value = [
                'foo/bar',
                'vapor:io',
            ]

            m = websocket.Message(id='testing', event='testing', data={})
            resp = await m.handle_request_tags()

            assert resp == {
                'id': 'testing',
                'event': 'response/tags',
                'data': mock_cmd.return_value,
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            'default',
            with_id_tags=False,
        )

    @pytest.mark.asyncio
    async def test_request_tags_data_ns(self):
        with asynctest.patch('synse_server.cmd.tags') as mock_cmd:
            mock_cmd.return_value = [
                'foo/bar',
                'vapor:io',
            ]

            m = websocket.Message(id='testing', event='testing', data={'ns': ['a', 'b', 'c']})
            resp = await m.handle_request_tags()

            assert resp == {
                'id': 'testing',
                'event': 'response/tags',
                'data': mock_cmd.return_value,
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            'a', 'b', 'c',
            with_id_tags=False,
        )

    @pytest.mark.asyncio
    async def test_request_tags_data_ids(self):
        with asynctest.patch('synse_server.cmd.tags') as mock_cmd:
            mock_cmd.return_value = [
                'foo/bar',
                'vapor:io',
            ]

            m = websocket.Message(id='testing', event='testing', data={'ids': True})
            resp = await m.handle_request_tags()

            assert resp == {
                'id': 'testing',
                'event': 'response/tags',
                'data': mock_cmd.return_value,
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            'default',
            with_id_tags=True,
        )

    @pytest.mark.asyncio
    async def test_request_info(self):
        with asynctest.patch('synse_server.cmd.info') as mock_cmd:
            mock_cmd.return_value = {
                'key': 'value',
            }

            m = websocket.Message(id='testing', event='testing', data={'device': '123'})
            resp = await m.handle_request_info()

            assert resp == {
                'id': 'testing',
                'event': 'response/info',
                'data': mock_cmd.return_value,
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            device_id='123',
        )

    @pytest.mark.asyncio
    async def test_request_info_error(self):
        with asynctest.patch('synse_server.cmd.info') as mock_cmd:
            mock_cmd.return_value = {
                'key': 'value',
            }

            m = websocket.Message(id='testing', event='testing', data={})

            with pytest.raises(errors.InvalidUsage):
                await m.handle_request_info()

        mock_cmd.assert_not_called()

    @pytest.mark.asyncio
    async def test_request_read_no_data(self):
        with asynctest.patch('synse_server.cmd.read') as mock_cmd:
            mock_cmd.return_value = [{
                'key': 'value',
            }]

            m = websocket.Message(id='testing', event='testing', data={})
            resp = await m.handle_request_read()

            assert resp == {
                'id': 'testing',
                'event': 'response/reading',
                'data': mock_cmd.return_value,
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tags=[],
        )

    @pytest.mark.asyncio
    async def test_request_read_data_ns(self):
        with asynctest.patch('synse_server.cmd.read') as mock_cmd:
            mock_cmd.return_value = [{
                'key': 'value',
            }]

            m = websocket.Message(id='testing', event='testing', data={'ns': 'foo'})
            resp = await m.handle_request_read()

            assert resp == {
                'id': 'testing',
                'event': 'response/reading',
                'data': mock_cmd.return_value,
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='foo',
            tags=[],
        )

    @pytest.mark.asyncio
    async def test_request_read_data_tags(self):
        with asynctest.patch('synse_server.cmd.read') as mock_cmd:
            mock_cmd.return_value = [{
                'key': 'value',
            }]

            m = websocket.Message(id='testing', event='testing', data={'tags': ['foo', 'bar']})
            resp = await m.handle_request_read()

            assert resp == {
                'id': 'testing',
                'event': 'response/reading',
                'data': mock_cmd.return_value,
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            ns='default',
            tags=['foo', 'bar'],
        )

    @pytest.mark.asyncio
    async def test_request_read_device(self):
        with asynctest.patch('synse_server.cmd.read_device') as mock_cmd:
            mock_cmd.return_value = {
                'key': 'value',
            }

            m = websocket.Message(id='testing', event='testing', data={'device': '123'})
            resp = await m.handle_request_read_device()

            assert resp == {
                'id': 'testing',
                'event': 'response/reading',
                'data': mock_cmd.return_value,
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            device_id='123',
        )

    @pytest.mark.asyncio
    async def test_request_read_device_error(self):
        with asynctest.patch('synse_server.cmd.read_device') as mock_cmd:
            mock_cmd.return_value = {
                'key': 'value',
            }

            m = websocket.Message(id='testing', event='testing', data={})

            with pytest.raises(errors.InvalidUsage):
                await m.handle_request_read_device()

        mock_cmd.assert_not_called()

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

            m = websocket.Message(id='testing', event='testing', data={})
            resp = await m.handle_request_read_cache()

            assert resp == {
                'id': 'testing',
                'event': 'response/reading',
                'data':[
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
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            start=None,
            end=None,
        )

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

            m = websocket.Message(id='testing', event='testing', data={'start': 'now'})
            resp = await m.handle_request_read_cache()

            assert resp == {
                'id': 'testing',
                'event': 'response/reading',
                'data': [
                    {
                        'value': 1,
                        'type': 'temperature',
                    }
                ],
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            start='now',
            end=None,
        )

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

            m = websocket.Message(id='testing', event='testing', data={'end': 'now'})
            resp = await m.handle_request_read_cache()

            assert resp == {
                'id': 'testing',
                'event': 'response/reading',
                'data': [
                    {
                        'value': 1,
                        'type': 'temperature',
                    },
                ],
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            start=None,
            end='now',
        )

    @pytest.mark.asyncio
    async def test_request_write_async(self):
        with asynctest.patch('synse_server.cmd.write_async') as mock_cmd:
            mock_cmd.return_value = {
                'key': 'value',
            }

            m = websocket.Message(
                id='testing',
                event='testing',
                data={'device': '123', 'payload': {'action': 'foo'}},
            )
            resp = await m.handle_request_write_async()

            assert resp == {
                'id': 'testing',
                'event': 'response/write_async',
                'data': mock_cmd.return_value,
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            device_id='123',
            payload={'action': 'foo'}
        )

    @pytest.mark.asyncio
    async def test_request_write_async_error_id(self):
        with asynctest.patch('synse_server.cmd.write_async') as mock_cmd:
            mock_cmd.return_value = {
                'key': 'value',
            }

            m = websocket.Message(id='testing', event='testing', data={'payload': {'action': 'foo'}})

            with pytest.raises(errors.InvalidUsage):
                await m.handle_request_write_async()

        mock_cmd.assert_not_called()

    @pytest.mark.asyncio
    async def test_request_write_async_error_payload(self):
        with asynctest.patch('synse_server.cmd.write_async') as mock_cmd:
            mock_cmd.return_value = {
                'key': 'value',
            }

            m = websocket.Message(id='testing', event='testing', data={'device': '123'})

            with pytest.raises(errors.InvalidUsage):
                await m.handle_request_write_async()

        mock_cmd.assert_not_called()

    @pytest.mark.asyncio
    async def test_request_write_sync(self):
        with asynctest.patch('synse_server.cmd.write_sync') as mock_cmd:
            mock_cmd.return_value = {
                'key': 'value',
            }

            m = websocket.Message(
                id='testing',
                event='testing',
                data={'device': '123', 'payload': {'action': 'foo'}},
            )
            resp = await m.handle_request_write_sync()

            assert resp == {
                'id': 'testing',
                'event': 'response/write_sync',
                'data': mock_cmd.return_value,
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with(
            device_id='123',
            payload={'action': 'foo'}
        )

    @pytest.mark.asyncio
    async def test_request_write_sync_error_id(self):
        with asynctest.patch('synse_server.cmd.write_sync') as mock_cmd:
            mock_cmd.return_value = {
                'key': 'value',
            }

            m = websocket.Message(id='testing', event='testing', data={'payload': {'action': 'foo'}})

            with pytest.raises(errors.InvalidUsage):
                await m.handle_request_write_sync()

        mock_cmd.assert_not_called()

    @pytest.mark.asyncio
    async def test_request_write_sync_error_payload(self):
        with asynctest.patch('synse_server.cmd.write_sync') as mock_cmd:
            mock_cmd.return_value = {
                'key': 'value',
            }

            m = websocket.Message(id='testing', event='testing', data={'device': '123'})

            with pytest.raises(errors.InvalidUsage):
                await m.handle_request_write_sync()

        mock_cmd.assert_not_called()

    @pytest.mark.asyncio
    async def test_request_transaction_no_data(self):
        with asynctest.patch('synse_server.cmd.transactions') as mock_cmd:
            mock_cmd.return_value = [{
                'key': 'value',
            }]

            m = websocket.Message(id='testing', event='testing', data={})
            resp = await m.handle_request_transaction()

            assert resp == {
                'id': 'testing',
                'event': 'response/transaction',
                'data': mock_cmd.return_value,
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with()

    @pytest.mark.asyncio
    async def test_request_transaction_with_data(self):
        with asynctest.patch('synse_server.cmd.transaction') as mock_cmd:
            mock_cmd.return_value = [{
                'key': 'value',
            }]

            m = websocket.Message(id='testing', event='testing', data={'transaction': 'foo'})
            resp = await m.handle_request_transaction()

            assert resp == {
                'id': 'testing',
                'event': 'response/transaction',
                'data': mock_cmd.return_value,
            }

        mock_cmd.assert_called_once()
        mock_cmd.assert_called_with('foo')


@pytest.mark.usefixtures('patch_utils_rfc3339now')
def test_error_no_exception():
    resp = websocket.error()

    assert json.loads(resp) == {
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

    assert json.loads(resp) == {
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

    assert json.loads(resp) == {
        'id': 3,
        'event': 'response/error',
        'data': {
            'http_code': 500,
            'description': 'test message',
            'timestamp': '2019-04-22T13:30:00Z',
            'context': 'uh oh',
        }
    }
