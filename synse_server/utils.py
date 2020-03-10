"""Synse Server utility and convenience methods."""

import datetime
from typing import Dict, List, Union

import sanic.response
import ujson

from synse_server import config


def normalize_write_ctx(data: Dict) -> None:
    """Normalize the given write context for consistent response formatting.

    The write context is the dictionary under the 'context' key which contains
    the reflected write data (action, data, transaction) which is included as
    part of the API write and transaction responses.

    The normalization process includes:
      * Ensuring the "data" field is encoded as utf-8
      * Ensuring that an empty "transaction" field is omitted from the response.
    """
    if 'context' not in data:
        return

    # Ensure the 'data' field is encoded as utf-8
    if 'data' in data['context']:
        if isinstance(data['context']['data'], bytes):
            data['context']['data'] = data['context']['data'].decode('utf-8')

    # Ensure an empty 'transaction' field is omitted
    if 'transaction' in data['context'] and not data['context']['transaction']:
        del data['context']['transaction']


def rfc3339now() -> str:
    """Create an RFC3339 formatted timestamp for the current UTC time.

    See Also:
        https://stackoverflow.com/a/8556555

    Returns:
        The RFC3339 formatted timestamp.
    """
    now = datetime.datetime.utcnow().replace(microsecond=0)
    return now.isoformat('T') + 'Z'


def _dumps(*arg, **kwargs) -> str:
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
        The given dictionary data dumped to a JSON string.
    """
    out = ujson.dumps(*arg, **kwargs)
    if not out.endswith('\n'):
        out += '\n'
    return out


def http_json_response(body: Union[Dict, List], **kwargs) -> sanic.response.HTTPResponse:
    """Create a JSON-encoded `HTTPResponse` for an HTTP endpoint response.

    Args:
        body: Data which will be encoded into a JSON HTTPResponse.
        **kwargs: Keyword arguments to pass to the response constructor.

    Returns:
        The Sanic endpoint response with the given body encoded as JSON.
    """
    if config.options.get('pretty_json'):
        return sanic.response.json(body, indent=2, dumps=_dumps, **kwargs)
    return sanic.response.json(body, **kwargs)
