"""Synse Server WebSocket API."""

import json

from sanic import Blueprint

from synse_server import cmd, errors, utils
from synse_server.i18n import _
from synse_server.log import logger

# Blueprint for the Synse v3 WebSocket API.
v3 = Blueprint('v3-websocket')


class Message:
    """"""

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

    async def response(self):
        """"""

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

    async def handle_request_status(self):
        """"""
        return {
            'id': self.id,
            'event': 'response/status',
            'data': await cmd.test(),
        }

    async def handle_request_version(self):
        """"""
        return {
            'id': self.id,
            'event': 'response/version',
            'data': await cmd.version(),
        }

    async def handle_request_config(self):
        """"""
        return {
            'id': self.id,
            'event': 'response/config',
            'data': await cmd.config(),
        }

    async def handle_request_plugin(self):
        """"""
        plugin_id = self.data.get('plugin')
        if not plugin_id:
            data = await cmd.plugins()
        else:
            data = await cmd.plugin(plugin_id)

        return {
            'id': self.id,
            'event': 'response/plugin',
            'data': data,
        }

    async def handle_request_plugin_health(self):
        """"""
        return {
            'id': self.id,
            'event': 'response/plugin_health',
            'data': await cmd.plugin_health(),
        }

    async def handle_request_scan(self):
        """"""
        ns = self.data.get('ns', 'default')
        tags = self.data.get('tags', [])
        force = self.data.get('force', False)
        sort_keys = 'plugin,sortIndex,id'

        return {
            'id': self.id,
            'event': 'response/scan',
            'data': await cmd.scan(
                ns=ns,
                tags=tags,
                sort=sort_keys,
                force=force,
            ),
        }

    async def handle_request_tags(self):
        """"""
        ns = self.data.get('ns', ['default'])
        ids = self.data.get('ids', False)

        return {
            'id': self.id,
            'event': 'response/tags',
            'data': await cmd.tags(*ns, with_id_tags=ids),
        }

    async def handle_request_info(self):
        """"""
        device = self.data.get('device')
        if device is None:
            raise errors.InvalidUsage('required data "device" not specified')

        return {
            'id': self.id,
            'event': 'response/info',
            'data': await cmd.info(device_id=device),
        }

    async def handle_request_read(self):
        """"""
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

    async def handle_request_read_device(self):
        """"""
        device = self.data.get('device')
        if device is None:
            raise errors.InvalidUsage('required data "device" not specified')

        return {
            'id': self.id,
            'event': 'response/reading',
            'data': await cmd.read_device(device_id=device),
        }

    async def handle_request_read_cache(self):
        """"""
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

    async def handle_request_write_async(self):
        """"""
        device = self.data.get('device')
        if device is None:
            raise errors.InvalidUsage('required data "device" not specified')

        payload = self.data.get('payload')
        if payload is None:
            raise errors.InvalidUsage('required data "payload" not specified')

        return {
            'id': self.id,
            'event': 'response/write_async',
            'data': await cmd.write_async(
                device_id=device,
                payload=payload,
            ),
        }

    async def handle_request_write_sync(self):
        """"""
        device = self.data.get('device')
        if device is None:
            raise errors.InvalidUsage('required data "device" not specified')

        payload = self.data.get('payload')
        if payload is None:
            raise errors.InvalidUsage('required data "payload" not specified')

        return {
            'id': self.id,
            'event': 'response/write_sync',
            'data': await cmd.write_sync(
                device_id=device,
                payload=payload,
            ),
        }

    async def handle_request_transaction(self):
        """"""
        transaction = self.data.get('transaction')
        if not transaction:
            data = await cmd.transactions()
        else:
            data = await cmd.transaction(transaction)

        return {
            'id': self.id,
            'event': 'response/transaction',
            'data': data,
        }


def error(msg_id=None, message=None, ex=None):
    """"""
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
    """"""

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
