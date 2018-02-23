"""Test the 'synse.routes.core' module's read route."""
# pylint: disable=redefined-outer-name,unused-argument

from synse import errors
from synse.version import __api_version__
from tests import utils

invalid_read_url = '/synse/{}/read/invalid-rack/invalid-board/invalid-device'.format(__api_version__)


def test_read_endpoint_invalid(app):
    """Test getting a invalid read response.

    We get a DEVICE_NOT_FOUND error because the rack, board, and
    device are used to make a composite ID for the device. If any
    one component is wrong, the ID composite device ID is wrong.
    """
    _, response = app.test_client.get(invalid_read_url)
    utils.test_error_json(response, errors.DEVICE_NOT_FOUND)


def test_read_endpoint_post_not_allowed(app):
    """Invalid request: POST"""
    _, response = app.test_client.post(invalid_read_url)
    assert response.status == 405


def test_read_endpoint_put_not_allowed(app):
    """Invalid request: PUT"""
    _, response = app.test_client.put(invalid_read_url)
    assert response.status == 405


def test_read_endpoint_delete_not_allowed(app):
    """Invalid request: DELETE"""
    _, response = app.test_client.delete(invalid_read_url)
    assert response.status == 405


def test_read_endpoint_patch_not_allowed(app):
    """Invalid request: PATCH"""
    _, response = app.test_client.patch(invalid_read_url)
    assert response.status == 405


def test_read_endpoint_head_not_allowed(app):
    """Invalid request: HEAD"""
    _, response = app.test_client.head(invalid_read_url)
    assert response.status == 405


def test_read_endpoint_options_not_allowed(app):
    """Invalid request: OPTIONS"""
    _, response = app.test_client.options(invalid_read_url)
    assert response.status == 405
