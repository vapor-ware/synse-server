"""Synse Server WebSocket API."""

import json

from sanic import Blueprint

from synse_server import cmd, errors, utils
from synse_server.i18n import _
from synse_server.log import logger

# Blueprint for the Synse v3 WebSocket API.
v3 = Blueprint('v3-websocket')


class Message:
    """Message manages WebSocket events and implements handling around the
    message receive/response.
    """

    def __init__(self, id, event, data):
        self.id = id
        self.event = event
        self.data = data

    @classmethod
    def from_json(cls, payload):
        """Create a new message from a WebSocket request payload.

        Args:
            payload (str): The request data.

        Returns:
            Message: A Message from the given request payload.
        """
        try:
            d = json.loads(payload)
        except Exception as e:
            logger.error(_('failed to load payload'), err=e)
            raise e

        return cls(
            id=d['id'],
            event=d['event'],
            data=d.get('data', {}),
        )

    async def response(self) -> str:
        """Generate the response for the Message's request data.

        Messages are passed along to their corresponding handler function, which is
        the function with the same name as the event type, prefixed with 'handle'.
        """

        # Generate the name of the handler function, e.g. "handle_request_status"
        handler = '_'.join(['handle'] + self.event.split('/'))

        if not hasattr(self, handler):
            return error(
                msg_id=self.id,
                message=f'unsupported event type: {self.event}',
            )

        try:
            logger.debug(_('processing websocket request'), handler=handler)
            return json.dumps(await getattr(self, handler)())
        except Exception as e:
            logger.error(_('error processing request'), err=e)
            return error(
                msg_id=self.id,
                ex=e,
            )

    # ---

    async def handle_request_status(self) -> dict:
        """WebSocket 'status' event message handler."""
        return {
            'id': self.id,
            'event': 'response/status',
            'data': await cmd.test(),
        }

    async def handle_request_version(self) -> dict:
        """WebSocket 'version' event message handler."""
        return {
            'id': self.id,
            'event': 'response/version',
            'data': await cmd.version(),
        }

    async def handle_request_config(self) -> dict:
        """WebSocket 'config' event message handler."""
        return {
            'id': self.id,
            'event': 'response/config',
            'data': await cmd.config(),
        }

    async def handle_request_plugin(self) -> dict:
        """WebSocket 'plugin' event message handler."""
        plugin_id = self.data.get('plugin')
        if plugin_id is None:
            raise errors.InvalidUsage('required data "plugin" not specified')

        return {
            'id': self.id,
            'event': 'response/plugin_info',
            'data': await cmd.plugin(plugin_id),
        }

    async def handle_request_plugins(self) -> dict:
        """WebSocket 'plugins' event message handler."""
        return {
            'id': self.id,
            'event': 'response/plugin_summary',
            'data': await cmd.plugins(),
        }

    async def handle_request_plugin_health(self) -> dict:
        """WebSocket 'plugin health' event message handler."""
        return {
            'id': self.id,
            'event': 'response/plugin_health',
            'data': await cmd.plugin_health(),
        }

    async def handle_request_scan(self) -> dict:
        """WebSocket 'scan' event message handler."""
        ns = self.data.get('ns', 'default')
        tags = self.data.get('tags', [])
        force = self.data.get('force', False)
        sort_keys = 'plugin,sortIndex,id'

        return {
            'id': self.id,
            'event': 'response/device_summary',
            'data': await cmd.scan(
                ns=ns,
                tags=tags,
                sort=sort_keys,
                force=force,
            ),
        }

    async def handle_request_tags(self) -> dict:
        """WebSocket 'tags' event message handler."""
        ns = self.data.get('ns', ['default'])
        ids = self.data.get('ids', False)

        return {
            'id': self.id,
            'event': 'response/tags',
            'data': await cmd.tags(*ns, with_id_tags=ids),
        }

    async def handle_request_info(self) -> dict:
        """WebSocket 'info' event message handler."""
        device = self.data.get('device')
        if device is None:
            raise errors.InvalidUsage('required data "device" not specified')

        return {
            'id': self.id,
            'event': 'response/device_info',
            'data': await cmd.info(device_id=device),
        }

    async def handle_request_read(self) -> dict:
        """WebSocket 'read' event message handler."""
        ns = self.data.get('ns', 'default')
        tags = self.data.get('tags', [])

        return {
            'id': self.id,
            'event': 'response/reading',
            'data': await cmd.read(
                ns=ns,
                tags=tags,
            ),
        }

    async def handle_request_read_device(self) -> dict:
        """WebSocket 'read device' event message handler."""
        device = self.data.get('device')
        if device is None:
            raise errors.InvalidUsage('required data "device" not specified')

        return {
            'id': self.id,
            'event': 'response/reading',
            'data': await cmd.read_device(device_id=device),
        }

    async def handle_request_read_cache(self) -> dict:
        """WebSocket 'read cache' event message handler."""
        start = self.data.get('start')
        end = self.data.get('end')

        # FIXME: should this return the whole list in one message? probably
        #   not.. we probably want to send in multiple messages..
        return {
            'id': self.id,
            'event': 'response/reading',
            'data': [x async for x in cmd.read_cache(
                start=start,
                end=end,
            )],
        }

    async def handle_request_write_async(self) -> dict:
        """WebSocket 'write async' event message handler."""
        device = self.data.get('device')
        if device is None:
            raise errors.InvalidUsage('required data "device" not specified')

        payload = self.data.get('payload')
        if payload is None:
            raise errors.InvalidUsage('required data "payload" not specified')

        return {
            'id': self.id,
            'event': 'response/transaction_info',
            'data': await cmd.write_async(
                device_id=device,
                payload=payload,
            ),
        }

    async def handle_request_write_sync(self) -> dict:
        """WebSocket 'write sync' event message handler."""
        device = self.data.get('device')
        if device is None:
            raise errors.InvalidUsage('required data "device" not specified')

        payload = self.data.get('payload')
        if payload is None:
            raise errors.InvalidUsage('required data "payload" not specified')

        return {
            'id': self.id,
            'event': 'response/transaction_status',
            'data': await cmd.write_sync(
                device_id=device,
                payload=payload,
            ),
        }

    async def handle_request_transaction(self) -> dict:
        """WebSocket 'transaction' event message handler."""
        transaction = self.data.get('transaction')
        if transaction is None:
            raise errors.InvalidUsage('required data "transaction" not specified')

        return {
            'id': self.id,
            'event': 'response/transaction_status',
            'data': await cmd.transaction(
                transaction,
            ),
        }

    async def handle_request_transactions(self) -> dict:
        """WebSocket 'transactions' event message handler."""
        return {
            'id': self.id,
            'event': 'response/transaction_list',
            'data': await cmd.transactions(),
        }


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


@v3.websocket('/v3/connect')
async def connect(request, ws):
    """Connect to the WebSocket API."""

    logger.info(_('new websocket connection'), source=request.ip)

    while True:
        r = await ws.recv()
        try:
            m = Message.from_json(r)
        except Exception as e:
            logger.error(_('error loading websocket message'), error=e)
            await ws.send(error(ex=e))
            continue

        logger.debug(_('got message'), id=m.id, type=m.event, data=m.data)

        try:
            resp = await m.response()
        except Exception as e:
            logger.error(_('error generating websocket response'), err=e)
            continue
        else:
            await ws.send(resp)
