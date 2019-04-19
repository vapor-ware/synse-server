"""Synse Server utility and convenience methods."""

import datetime

import ujson
from sanic.response import json as sjson

from synse_server import config


def rfc3339now():
    """Create an RFC3339 formatted timestamp for the current UTC time.

    See Also:
        https://stackoverflow.com/a/8556555

    Returns:
        str: The RFC3339 formatted timestamp.
    """
    now = datetime.datetime.utcnow().replace(microsecond=0)
    return now.isoformat('T') + 'Z'


def _dumps(*arg, **kwargs):
    """Custom JSON dumps implementation to be used when pretty printing.

    The `sanic.response` json function uses `ujson.dumps` as its default dumps
    method. It appears that this does not include a new line after the
    dumped JSON. When curl-ing or otherwise getting Synse Server data from
    the command line, this can cause the shell prompt to be placed on the
    same line as the last line of JSON output. While not necessarily a bad
    thing, it can be inconvenient.

    This custom function adds in the newline, if it doesn't exist, so that
    the shell prompt will start on a new line.

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


def http_json_response(body, **kwargs):
    """Create a JSON-encoded `HTTPResponse` for an HTTP endpoint response.

    Args:
        body (dict | list): Data that will be encoded into a JSON HTTPResponse.
        **kwargs: Keyword arguments to pass to the response constructor.

    Returns:
        sanic.HTTPResponse: The Sanic endpoint response with the given body
            encoded as JSON.
    """
    if config.options.get('pretty_json'):
        return sjson(body, indent=2, dumps=_dumps, **kwargs)
    return sjson(body, **kwargs)
