"""Synse Server WebSocket API."""

from sanic import Blueprint

# Blueprint for the Synse v3 WebSocket API.
v3 = Blueprint('v3-websocket')


@v3.websocket('/v3/connect')
async def connect(request, ws):
    """"""
    data = 'hello!'
    while True:
        print('Sending: ' + data)
        await ws.send(data)
        data = await ws.recv()
        print('Received: ' + data)
