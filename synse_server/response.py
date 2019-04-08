"""Utilities and helpers for application endpoint responses."""

import ujson
from sanic.response import json as sjson

import synse_server
import synse_server.config
import synse_server.plugin
from synse_server import utils


# FIXME (etd) - could move to utils
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


# FIXME (etd) - could move to utils
def json(body, **kwargs):
    """Create a JSON-encoded `HTTPResponse` for an endpoint.

    Args:
        body (dict): A dictionary of data that will be encoded into a JSON
            HTTPResponse.
        **kwargs: Keyword arguments to pass to the response constructor.

    Returns:
        sanic.HTTPResponse: The Sanic endpoint response with the given body
            encoded as JSON.
    """
    if synse_server.config.options.get('pretty_json'):
        return sjson(body, indent=2, dumps=_dumps, **kwargs)
    return sjson(body, **kwargs)


# TODO: move to scheme.py after removing the scheme dir

def test():
    """Generate the test response data.

    Returns:
        dict: A dictionary representation of the test response.
    """
    return {
        'status': 'ok',
        'timestamp': utils.rfc3339now(),
    }


def version():
    """Generate the version response data.

    Returns:
        dict: A dictionary representation of the version response.
    """
    return {
        'version': synse_server.__version__,
        'api_version': synse_server.__api_version__,
    }


def config():
    """Generate the config response data.

    Returns:
        dict: A dictionary representation of the config response.
    """
    return {k: v for k, v in synse_server.config.options.config.items() if not k.startswith('_')}


def plugin_summary():
    """Generate the plugin summary response data.

    Returns:
        list[dict]: A list of dictionary representations of the plugin
        summary response(s).
    """
    summaries = []
    for p in synse_server.plugin.manager:
        summaries.append({
            'active': True,
            'description': p.description,
            'id': p.id,
            'maintainer': p.maintainer,
            'name': p.name,
        })

    return summaries


def plugin(id):
    """Generate the plugin response data.

    Args:
        id (str): The ID of the plugin to get information for.

    Returns:
        dict: A dictionary representation of the plugin response.
    """
    pass


def plugin_health():
    """Generate the plugin health response data.

    Returns:
         dict: A dictionary representation of the plugin health.
    """
    pass


def scan():
    """Generate the scan response data.

    Returns:
         list[dict]: A list of dictionary representations of device
         summary response(s).
    """
    pass


def tags():
    """Generate the tags response data.

    Returns:
        list[string]: A list of all tags currently associated with devices.
    """
    pass


def info():
    """Generate the device info response data.

    Returns:
        dict: A dictionary representation of the device info response.
    """
    pass


def readings():
    """Generate the readings response data.

    Returns:
        list[dict]: A list of dictionary representations of device reading
        response(s).
    """
    pass


def write():
    """Generate the asynchronous write response data.

    Returns:
         list[dict]: A list of dictionary representations of asynchronous
         write response(s).
    """
    pass


def transaction():
    """Generate the transaction response data.

    Returns:
        dict: A dictionary representation of the transaction response.
    """
    pass
