"""Utilities for application responses."""

import ujson
from sanic.response import json as sjson

from synse import config


def _dumps(*arg, **kwargs):
    """Custom JSON dumps implementation to be used when pretty printing.

    sanic.response's json function uses ujson.dumps as its default dumps
    method. It appears that this does not include a new line after the
    dumped JSON. When curl-ing or otherwise getting Synse Server data from
    the command line, this can cause the shell prompt to be placed on the
    same line as the last line of JSON output.

    This custom function adds in the newline, if it doesn't exist, so that
    the shell prompt will always start on a new line.

    Args:
        *arg: Arguments for ujson.dumps.
        **kwargs: Keyword arguments for ujson.dumps.

    Returns:
        str: The given dictionary data dumped to a JSON string.
    """
    out = ujson.dumps(*arg, **kwargs)
    if not out.endswith('\n'):
        out += '\n'
    return out


def json(body, **kwargs):
    """Create a JSON-encoded HTTPResponse for an endpoint.

    Args:
        body (dict): A dictionary of data that will be encoded into a JSON
            HTTPResponse.

    Returns:
        sanic.HTTPResponse: The Sanic endpoint response with the given body
            encoded as JSON.
    """
    if config.options.get('pretty_json'):
        return sjson(body, indent=2, dumps=_dumps, **kwargs)
    return sjson(body, **kwargs)
