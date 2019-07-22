#!/usr/bin/env python

import asyncio
import json
import websockets


async def main():
    async with websockets.connect('ws://localhost:5000/v3/connect') as ws:
        await ws.send(json.dumps({
            'id': 0,
            'event': 'request/read_stream',
            'data': {
                # 'ids': ['0570c34a-32fd-56c5-a0a3-d4a229e89536']
            },
        }))

        print('starting recv loop')
        while True:
            try:
                resp = await ws.recv()
                r = json.loads(resp)
                print('{}] {}\t\t{:15}{}'.format(
                    r['data']['timestamp'],
                    r['data']['device'],
                    r['data']['type'],
                    r['data']['value'],
                ))
            except KeyboardInterrupt:
                print('error!')
                await ws.close(code=1001, reason='keyboard interrupt')
                return

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(main())
