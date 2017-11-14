"""Utility functions for Synse Server tests.
"""

import ujson
from sanic.request import Request


def make_request(url, data=None):
    """Create a Sanic request object.

    Args:
        url (str): The URL of the request.
        data (dict): [optional] Any data to dump into the request body.

    Returns:
        sanic.request.Request: A simple Request object.
    """
    r = Request(
        url_bytes=url.encode('ascii'),
        headers={},
        version=None,
        method=None,
        transport=None
    )

    if data is not None:
        r.body = ujson.dumps(data)

    return r
