"""Test the 'synse.routes.aliases' Synse Server module's fan route."""
# pylint: disable=redefined-outer-name,unused-argument

import pytest
import ujson

from synse import config, errors, factory
from synse.version import __api_version__

invalid_fan_route_url = '/synse/{}/fan/invalid-rack/invalid-board/invalid-device'.format(__api_version__)


@pytest.fixture()
def app():
    """Fixture to get a Synse Server application instance."""
    yield factory.make_app()


def test_fan_endpoint_invalid(app):
    """Test getting a invalid fan response.

    Details:
        In this case, rack, board, device are invalid.
        However, the returned error should be DEVICE_NOT_FOUND,
        instead of RACK_NOT_FOUND, even though it is also true.

        There is no need to check for a request with query paramter(s)
        because the device is not found anyway.
    """
    _, response = app.test_client.get(invalid_fan_route_url)

    assert response.status == 500

    data = ujson.loads(response.text)

    assert 'http_code' in data
    assert 'error_id' in data
    assert 'description' in data
    assert 'timestamp' in data
    assert 'context' in data

    assert data['http_code'] == 500
    assert data['error_id'] == errors.DEVICE_NOT_FOUND


def test_fan_endpoint_post_not_allowed(app):
    """Invalid request: POST"""
    _, response = app.test_client.post(invalid_fan_route_url)
    assert response.status == 405


def test_fan_endpoint_put_not_allowed(app):
    """Invalid request: PUT"""
    _, response = app.test_client.put(invalid_fan_route_url)
    assert response.status == 405


def test_fan_endpoint_delete_not_allowed(app):
    """Invalid request: DELETE"""
    _, response = app.test_client.delete(invalid_fan_route_url)
    assert response.status == 405


def test_fan_endpoint_patch_not_allowed(app):
    """Invalid request: PATCH"""
    _, response = app.test_client.patch(invalid_fan_route_url)
    assert response.status == 405


def test_fan_endpoint_head_not_allowed(app):
    """Invalid request: HEAD"""
    _, response = app.test_client.head(invalid_fan_route_url)
    assert response.status == 405


def test_fan_endpoint_options_not_allowed(app):
    """Invalid request: OPTIONS"""
    _, response = app.test_client.options(invalid_fan_route_url)
    assert response.status == 405
