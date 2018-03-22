"""Utility functions for Synse Server tests."""

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


def test_error_json(response, error_id, status_code=500):
    """Test utility for validating Synse Server error JSON responses."""

    assert response.status == status_code

    response_data = ujson.loads(response.text)

    assert 'http_code' in response_data
    assert 'error_id' in response_data
    assert 'description' in response_data
    assert 'timestamp' in response_data
    assert 'context' in response_data

    assert response_data['http_code'] == status_code
    assert response_data['error_id'] == error_id
