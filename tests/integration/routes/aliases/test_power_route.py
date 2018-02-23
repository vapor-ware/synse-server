"""Test the 'synse.routes.aliases' module's power route."""
# pylint: disable=redefined-outer-name,unused-argument

from synse import errors
from synse.version import __api_version__
from tests import utils

invalid_power_route_url = '/synse/{}/power/invalid-rack/invalid-board/invalid-device'.format(__api_version__)


def test_power_endpoint_invalid(app):
    """Get power info for a nonexistent device."""
    _, response = app.test_client.get(invalid_power_route_url)
    utils.test_error_json(response, errors.DEVICE_NOT_FOUND)


def test_power_endpoint_post_not_allowed(app):
    """Invalid request: POST"""
    _, response = app.test_client.post(invalid_power_route_url)
    assert response.status == 405


def test_power_endpoint_put_not_allowed(app):
    """Invalid request: PUT"""
    _, response = app.test_client.put(invalid_power_route_url)
    assert response.status == 405


def test_power_endpoint_delete_not_allowed(app):
    """Invalid request: DELETE"""
    _, response = app.test_client.delete(invalid_power_route_url)
    assert response.status == 405


def test_power_endpoint_patch_not_allowed(app):
    """Invalid request: PATCH"""
    _, response = app.test_client.patch(invalid_power_route_url)
    assert response.status == 405


def test_power_endpoint_head_not_allowed(app):
    """Invalid request: HEAD"""
    _, response = app.test_client.head(invalid_power_route_url)
    assert response.status == 405


def test_power_endpoint_options_not_allowed(app):
    """Invalid request: OPTIONS"""
    _, response = app.test_client.options(invalid_power_route_url)
    assert response.status == 405
