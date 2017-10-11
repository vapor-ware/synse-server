"""

"""

from sanic.response import json as sjson

from synse import config


def json(body, **kwargs):
    """

    Args:
        body (dict):
    """
    if config.options.get('pretty_json'):
        return sjson(body, indent=2, **kwargs)
    return sjson(body, **kwargs)
