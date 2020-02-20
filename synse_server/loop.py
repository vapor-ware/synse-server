"""Asyncio loop used by Synse Server.

This loop is defined in its own package so components sharing the
loop (Sanic, asyncio locks, etc) can access it easily without
running into import loops.
"""

import asyncio

synse_loop = asyncio.get_event_loop()
