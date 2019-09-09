"""Synse Server WebSocket API."""

import asyncio
import json

from sanic import Blueprint
from sanic.websocket import ConnectionClosed

from synse_server import cmd, errors, utils
from synse_server.i18n import _
from synse_server.log import logger

# Blueprint for the Synse v3 WebSocket API.
v3 = Blueprint('v3-websocket')


@v3.websocket('/v3/connect')
async def connect(request, ws):
    """Connect to the WebSocket API."""

    logger.info(_('new websocket connection'), source=request.ip)

    handler = MessageHandler(ws)
    await handler.run()


class Payload:
    """Payload describes the message that was received on a WebSocket connection."""

    def __init__(self, data) -> None:
        try:
            d = json.loads(data)
        except Exception as e:
            logger.error(_('failed to load payload'), err=e)
            raise

        if 'id' not in d:
            raise ValueError('expected "id" in websocket payload, but not found')
        if 'event' not in d:
            raise ValueError('expected "event" in websocket payload, but not found')

        self.id = d['id']
        self.event = d['event']
        self.data = d.get('data', {})

    def __str__(self) -> str:
        return f'<Payload id={self.id} event={self.event} data={self.data}>'

    def __repr__(self) -> str:
        return self.__str__()


def error(msg_id=None, message=None, ex=None) -> str:
    """A utility function to generate error response messages for
    errors returned via the WebSocket API.

    Args:
        msg_id (int): The ID of the message. If there is no message
            ID parsed yet or otherwise known, this will default to -1.
        message (str): The message to use as the error description.
        ex (Exception): The exception that caused the return error.

    Return:
        str: Serialized JSON string of the error message.
    """
    message_id = msg_id or -1
    msg = message or 'An unexpected error occurred.'

    if ex is None:
        data = {
            'description': msg,
            'timestamp': utils.rfc3339now(),
        }
    elif isinstance(ex, errors.SynseError):
        data = ex.make_response()
    else:
        data = {
            'http_code': 500,
            'description': msg,
            'timestamp': utils.rfc3339now(),
            'context': str(ex),
        }

    return json.dumps({
        'id': message_id,
        'event': 'response/error',
        'data': data,
    })


class MessageHandler:
    """A handler to receive and send messages on a WebSocket session.

    Args:
        ws (websockets.WebsocketCommonProtocol): The WebSocket for the request session
            which the MessageHandler will manage.
    """

    def __init__(self, ws):
        self.ws = ws

        # When the websocket is cancelled or terminates, ensure that the MessageHandler
        # associated with that websocket is stopped and cleaned up.
        if ws.close_connection_task is not None:
            ws.close_connection_task.add_done_callback(self.stop)

        # todo - if this don't work, just use threads.
        self.tasks = []

    async def run(self):
        logger.debug(_('running message handler for websocket'), host=self.ws.host)
        async for message in self.ws:
            try:
                p = Payload(message)
            except Exception as e:
                logger.error(_('error loading websocket message'), error=e)
                await self.ws.send(error(ex=e))
                continue

            logger.debug(_('got message'), payload=p)
            try:
                await self.dispatch(p)
            except Exception as e:
                logger.error(_('error generating websocket response'), err=e)
                continue

    def stop(self, *args, **kwargs):
        """Stop the MessageHandler.

        The MessageHandler will be stopped when the WebSocket connection is closed.
        This will terminate any tasks and threads which are associated with the
        handler.
        """
        logger.debug('stopping message handler for websocket', host=self.ws.host)

        for t in self.tasks:
            t.cancel()

    async def dispatch(self, payload):
        """Generate the response for the Message's request data.

        Messages are passed along to their corresponding handler function, which is
        the function with the same name as the event type, prefixed with 'handle'.

        Args:
            payload (Payload): The message payload received from the WebSocket.
        """

        # Generate the name of the handler function, e.g. "handle_request_status"
        handler = '_'.join(['handle'] + payload.event.split('/'))

        if not hasattr(self, handler):
            await self.ws.send(error(
                msg_id=payload.id,
                message=f'unsupported event type: {payload.event}',
            ))
            return

        try:
            logger.debug(_('processing websocket request'), handler=handler)
            await getattr(self, handler)(payload)
        except asyncio.CancelledError:
            logger.info(_('websocket request cancelled'), handler=handler)
            return
        except Exception as e:
            logger.error(_('error processing request'), err=e)
            await self.ws.send(error(
                msg_id=payload.id,
                ex=e,
            ))

    # ---

    async def handle_request_status(self, payload):
        """WebSocket 'status' event message handler.

        Args:
            payload (Payload): The message payload received from the WebSocket.
        """
        await self.ws.send(json.dumps({
            'id': payload.id,
            'event': 'response/status',
            'data': await cmd.test(),
        }))

    async def handle_request_version(self, payload):
        """WebSocket 'version' event message handler.

        Args:
            payload (Payload): The message payload received from the WebSocket.
        """
        await self.ws.send(json.dumps({
            'id': payload.id,
            'event': 'response/version',
            'data': await cmd.version(),
        }))

    async def handle_request_config(self, payload):
        """WebSocket 'config' event message handler.

        Args:
            payload (Payload): The message payload received from the WebSocket.
        """
        await self.ws.send(json.dumps({
            'id': payload.id,
            'event': 'response/config',
            'data': await cmd.config(),
        }))

    async def handle_request_plugin(self, payload):
        """WebSocket 'plugin' event message handler.

        Args:
            payload (Payload): The message payload received from the WebSocket.
        """
        plugin_id = payload.data.get('plugin')
        if plugin_id is None:
            raise errors.InvalidUsage('required data "plugin" not specified')

        await self.ws.send(json.dumps({
            'id': payload.id,
            'event': 'response/plugin_info',
            'data': await cmd.plugin(plugin_id),
        }))

    async def handle_request_plugins(self, payload):
        """WebSocket 'plugins' event message handler.

        Args:
            payload (Payload): The message payload received from the WebSocket.
        """
        await self.ws.send(json.dumps({
            'id': payload.id,
            'event': 'response/plugin_summary',
            'data': await cmd.plugins(),
        }))

    async def handle_request_plugin_health(self, payload):
        """WebSocket 'plugin health' event message handler.

        Args:
            payload (Payload): The message payload received from the WebSocket.
        """
        await self.ws.send(json.dumps({
            'id': payload.id,
            'event': 'response/plugin_health',
            'data': await cmd.plugin_health(),
        }))

    async def handle_request_scan(self, payload):
        """WebSocket 'scan' event message handler.

        Args:
            payload (Payload): The message payload received from the WebSocket.
        """
        ns = payload.data.get('ns', 'default')
        tags = payload.data.get('tags', [])
        force = payload.data.get('force', False)
        sort_keys = 'plugin,sortIndex,id'

        # If tags are specified and all elements in the tags parameter
        # are strings, they are part of a single tag group. Nest them
        # appropriately.
        if len(tags) != 0 and all(isinstance(t, str) for t in tags):
            tags = [tags]

        await self.ws.send(json.dumps({
            'id': payload.id,
            'event': 'response/device_summary',
            'data': await cmd.scan(
                ns=ns,
                tag_groups=tags,
                sort=sort_keys,
                force=force,
            ),
        }))

    async def handle_request_tags(self, payload):
        """WebSocket 'tags' event message handler.

        Args:
            payload (Payload): The message payload received from the WebSocket.
        """
        ns = payload.data.get('ns', ['default'])
        ids = payload.data.get('ids', False)

        await self.ws.send(json.dumps({
            'id': payload.id,
            'event': 'response/tags',
            'data': await cmd.tags(*ns, with_id_tags=ids),
        }))

    async def handle_request_info(self, payload):
        """WebSocket 'info' event message handler.

        Args:
            payload (Payload): The message payload received from the WebSocket.
        """
        device = payload.data.get('device')
        if device is None:
            raise errors.InvalidUsage('required data "device" not specified')

        await self.ws.send(json.dumps({
            'id': payload.id,
            'event': 'response/device_info',
            'data': await cmd.info(device_id=device),
        }))

    async def handle_request_read(self, payload):
        """WebSocket 'read' event message handler.

        Args:
            payload (Payload): The message payload received from the WebSocket.
        """
        ns = payload.data.get('ns', 'default')
        tags = payload.data.get('tags', [])

        # If tags are specified and all elements in the tags parameter
        # are strings, they are part of a single tag group. Nest them
        # appropriately.
        if len(tags) != 0 and all(isinstance(t, str) for t in tags):
            tags = [tags]

        await self.ws.send(json.dumps({
            'id': payload.id,
            'event': 'response/reading',
            'data': await cmd.read(
                ns=ns,
                tag_groups=tags,
            ),
        }))

    async def handle_request_read_device(self, payload):
        """WebSocket 'read device' event message handler.

        Args:
            payload (Payload): The message payload received from the WebSocket.
        """
        device = payload.data.get('device')
        if device is None:
            raise errors.InvalidUsage('required data "device" not specified')

        await self.ws.send(json.dumps({
            'id': payload.id,
            'event': 'response/reading',
            'data': await cmd.read_device(device_id=device),
        }))

    async def handle_request_read_cache(self, payload):
        """WebSocket 'read cache' event message handler.

        Args:
            payload (Payload): The message payload received from the WebSocket.
        """
        start = payload.data.get('start')
        end = payload.data.get('end')

        # FIXME: should this return the whole list in one message? probably
        #   not.. we probably want to send in multiple messages..
        #   (etd) - this is now doable since we have direct access to the ws instance
        await self.ws.send(json.dumps({
            'id': payload.id,
            'event': 'response/reading',
            'data': [x async for x in cmd.read_cache(
                start=start,
                end=end,
            )],
        }))

    async def handle_request_read_stream(self, payload):
        """WebSocket 'read stream' event message handler.

        Args:
            payload (Payload): The message payload received from the WebSocket.
        """
        ids = payload.data.get('ids')
        tag_groups = payload.data.get('tag_groups')
        stop = payload.data.get('stop', False)

        if stop:
            for t in self.tasks:
                t.cancel()
            return

        async def send_readings():
            async for reading in cmd.read_stream(self.ws, ids, tag_groups):
                try:
                    await self.ws.send(json.dumps({
                        'id': payload.id,
                        'event': 'response/reading',
                        'data': reading,
                    }))
                except ConnectionClosed:
                    logger.info(_('websocket raised ConnectionClosed - terminating read stream'))
                    return

        t = asyncio.ensure_future(send_readings())
        self.tasks.append(t)

    async def handle_request_write_async(self, payload):
        """WebSocket 'write async' event message handler.

        Args:
            payload (Payload): The message payload received from the WebSocket.
        """
        device = payload.data.get('device')
        if device is None:
            raise errors.InvalidUsage('required data "device" not specified')

        data = payload.data.get('payload')
        if data is None:
            raise errors.InvalidUsage('required data "payload" not specified')

        await self.ws.send(json.dumps({
            'id': payload.id,
            'event': 'response/transaction_info',
            'data': await cmd.write_async(
                device_id=device,
                payload=data,
            ),
        }))

    async def handle_request_write_sync(self, payload):
        """WebSocket 'write sync' event message handler.

        Args:
            payload (Payload): The message payload received from the WebSocket.
        """
        device = payload.data.get('device')
        if device is None:
            raise errors.InvalidUsage('required data "device" not specified')

        data = payload.data.get('payload')
        if data is None:
            raise errors.InvalidUsage('required data "payload" not specified')

        await self.ws.send(json.dumps({
            'id': payload.id,
            'event': 'response/transaction_status',
            'data': await cmd.write_sync(
                device_id=device,
                payload=data,
            ),
        }))

    async def handle_request_transaction(self, payload):
        """WebSocket 'transaction' event message handler.

        Args:
            payload (Payload): The message payload received from the WebSocket.
        """
        transaction = payload.data.get('transaction')
        if transaction is None:
            raise errors.InvalidUsage('required data "transaction" not specified')

        await self.ws.send(json.dumps({
            'id': payload.id,
            'event': 'response/transaction_status',
            'data': await cmd.transaction(
                transaction,
            ),
        }))

    async def handle_request_transactions(self, payload):
        """WebSocket 'transactions' event message handler.

        Args:
            payload (Payload): The message payload received from the WebSocket.
        """
        await self.ws.send(json.dumps({
            'id': payload.id,
            'event': 'response/transaction_list',
            'data': await cmd.transactions(),
        }))
