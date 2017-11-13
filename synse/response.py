"""Utilities for application responses.
"""

from sanic.response import json as sjson

from synse import config


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
        return sjson(body, indent=2, **kwargs)
    return sjson(body, **kwargs)
