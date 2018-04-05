"""Test the 'synse.routes.core' module's info route."""
# pylint: disable=redefined-outer-name,unused-argument

from synse import errors
from synse.version import __api_version__
from tests import utils

info_url = '/synse/{}/info'.format(__api_version__)
invalid_rack_info_url = '{}/invalid-rack'.format(info_url)
invalid_board_info_url = '{}/invalid-board'.format(invalid_rack_info_url)
invalid_device_info_url = '{}/invalid-device'.format(invalid_board_info_url)


def test_rack_info_endpoint_invalid(app):
    """Issue a request for a nonexistent rack."""
    _, response = app.test_client.get(invalid_rack_info_url)
    utils.test_error_json(response, errors.RACK_NOT_FOUND, 404)


def test_rack_info_endpoint_post_not_allowed(app):
    """Invalid request: POST"""
    _, response = app.test_client.post(invalid_rack_info_url)
    assert response.status == 405


def test_rack_info_endpoint_put_not_allowed(app):
    """Invalid request: PUT"""
    _, response = app.test_client.put(invalid_rack_info_url)
    assert response.status == 405


def test_rack_info_endpoint_delete_not_allowed(app):
    """Invalid request: DELETE"""
    _, response = app.test_client.delete(invalid_rack_info_url)
    assert response.status == 405


def test_rack_info_endpoint_patch_not_allowed(app):
    """Invalid request: PATCH"""
    _, response = app.test_client.patch(invalid_rack_info_url)
    assert response.status == 405


def test_rack_info_endpoint_head_not_allowed(app):
    """Invalid request: HEAD"""
    _, response = app.test_client.head(invalid_rack_info_url)
    assert response.status == 405


def test_rack_info_endpoint_options_not_allowed(app):
    """Invalid request: OPTIONS"""
    _, response = app.test_client.options(invalid_rack_info_url)
    assert response.status == 405


def test_board_info_endpoint_invalid(app):
    """Issue a request for a nonexistent rack/board.

    While both board and rack do not exist, we get the RACK_NOT_FOUND
    error because of the lookup order.
    """
    _, response = app.test_client.get(invalid_board_info_url)
    utils.test_error_json(response, errors.RACK_NOT_FOUND, 404)


def test_board_info_endpoint_post_not_allowed(app):
    """Invalid request: POST"""
    _, response = app.test_client.post(invalid_board_info_url)
    assert response.status == 405


def test_board_info_endpoint_put_not_allowed(app):
    """Invalid request: PUT"""
    _, response = app.test_client.put(invalid_board_info_url)
    assert response.status == 405


def test_board_info_endpoint_delete_not_allowed(app):
    """Invalid request: DELETE"""
    _, response = app.test_client.delete(invalid_board_info_url)
    assert response.status == 405


def test_board_info_endpoint_patch_not_allowed(app):
    """Invalid request: PATCH"""
    _, response = app.test_client.patch(invalid_board_info_url)
    assert response.status == 405


def test_board_info_endpoint_head_not_allowed(app):
    """Invalid request: HEAD"""
    _, response = app.test_client.head(invalid_board_info_url)
    assert response.status == 405


def test_board_info_endpoint_options_not_allowed(app):
    """Invalid request: OPTIONS"""
    _, response = app.test_client.options(invalid_board_info_url)
    assert response.status == 405


def test_device_info_endpoint_invalid(app):
    """Issue a request for a nonexistent rack/board/device.

    While device, board, and rack do not exist, we get the RACK_NOT_FOUND
    error because of the lookup order.
    """
    _, response = app.test_client.get(invalid_device_info_url)
    utils.test_error_json(response, errors.RACK_NOT_FOUND, 404)


def test_device_info_endpoint_post_not_allowed(app):
    """Invalid request: POST"""
    _, response = app.test_client.post(invalid_device_info_url)
    assert response.status == 405


def test_device_info_endpoint_put_not_allowed(app):
    """Invalid request: PUT"""
    _, response = app.test_client.put(invalid_device_info_url)
    assert response.status == 405


def test_device_info_endpoint_delete_not_allowed(app):
    """Invalid request: DELETE"""
    _, response = app.test_client.delete(invalid_device_info_url)
    assert response.status == 405


def test_device_info_endpoint_patch_not_allowed(app):
    """Invalid request: PATCH"""
    _, response = app.test_client.patch(invalid_device_info_url)
    assert response.status == 405


def test_device_info_endpoint_head_not_allowed(app):
    """Invalid request: HEAD"""
    _, response = app.test_client.head(invalid_device_info_url)
    assert response.status == 405


def test_device_info_endpoint_options_not_allowed(app):
    """Invalid request: OPTIONS"""
    _, response = app.test_client.options(invalid_device_info_url)
    assert response.status == 405
