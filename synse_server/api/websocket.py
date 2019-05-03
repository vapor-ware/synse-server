"""Synse Server WebSocket API."""

import json
from sanic import Blueprint

from synse_server import utils, cmd
from synse_server.log import logger
from synse_server.i18n import _

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
            logger.error('failed to load payload', err=e)
            raise e

        return cls(
            id=d['id'],
            event=d['event'],
            data=d.get('data', {}),
        )

    async def response(self):
        """"""

        handler = '_'.join(['handle'] + self.event.split('/'))

        if not hasattr(self, handler):
            return json.dumps({
                'id': 0,
                'event': 'response/error',
                'data': {
                    'description': 'invalid user input',
                    'timestamp': utils.rfc3339now(),
                    'context': f'unsupported event type: {self.event}',
                }
            })

        return json.dumps(await getattr(self, handler)())

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
            # TODO: can probably have a helper or series of helpers to generate
            #   error responses.
            await ws.send(json.dumps({
                'id': 0,
                'event': 'response/error',
                'data': {
                    'description': 'invalid user input',
                    'timestamp': utils.rfc3339now(),
                    'context': str(e),
                }
            }))
            continue

        logger.debug("got message", id=m.id, type=m.event, data=m.data)

        await ws.send(
            await m.response(),
        )

