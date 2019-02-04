"""Test the 'synse_server.routes.aliases' module's lock route."""
# pylint: disable=redefined-outer-name,unused-argument

from synse_server import errors
from synse_server.version import __api_version__
from tests import utils

invalid_lock_route_url = '/synse/{}/lock/invalid-rack/invalid-board/invalid-device'.format(__api_version__)


def test_lock_endpoint_invalid(app):
    """Get lock info for a nonexistent device."""
    _, response = app.test_client.get(invalid_lock_route_url)
    utils.test_error_json(response, errors.DEVICE_NOT_FOUND, 404)


def test_lock_endpoint_post_not_allowed(app):
    """Invalid request: POST"""
    _, response = app.test_client.post(invalid_lock_route_url)
    assert response.status == 405


def test_lock_endpoint_put_not_allowed(app):
    """Invalid request: PUT"""
    _, response = app.test_client.put(invalid_lock_route_url)
    assert response.status == 405


def test_lock_endpoint_delete_not_allowed(app):
    """Invalid request: DELETE"""
    _, response = app.test_client.delete(invalid_lock_route_url)
    assert response.status == 405


def test_lock_endpoint_patch_not_allowed(app):
    """Invalid request: PATCH"""
    _, response = app.test_client.patch(invalid_lock_route_url)
    assert response.status == 405


def test_lock_endpoint_head_not_allowed(app):
    """Invalid request: HEAD"""
    _, response = app.test_client.head(invalid_lock_route_url)
    assert response.status == 405


def test_lock_endpoint_options_not_allowed(app):
    """Invalid request: OPTIONS"""
    _, response = app.test_client.options(invalid_lock_route_url)
    assert response.status == 405
