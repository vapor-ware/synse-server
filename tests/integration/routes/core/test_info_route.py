"""Test the 'synse.routes.core' Synse Server module's info route."""
# pylint: disable=redefined-outer-name,unused-argument

import pytest
import ujson

from synse import errors, factory
from synse.version import __api_version__

info_url = '/synse/{}/info'.format(__api_version__)
invalid_rack_info_url = '{}/invalid-rack'.format(info_url)
invalid_board_info_url = '{}/invalid-board'.format(invalid_rack_info_url)
invalid_device_info_url = '{}/invalid-device'.format(invalid_board_info_url)


@pytest.fixture()
def app():
    """Fixture to get a Synse Server application instance."""
    yield factory.make_app()


def test_rack_info_endpoint_invalid(app):
    """Test getting a invalid rack info response.

    Details:
        In this case, rack is invalid.
        The retuned error should be RACK_NOT_FOUND.
    """
    _, response = app.test_client.get(invalid_rack_info_url)

    assert response.status == 500

    data = ujson.loads(response.text)

    assert 'http_code' in data
    assert 'error_id' in data
    assert 'description' in data
    assert 'timestamp' in data
    assert 'context' in data

    assert data['http_code'] == 500
    assert data['error_id'] == errors.RACK_NOT_FOUND


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
    """Test getting a board info response.

    Details:
        In this case, rack and board are invalid.
        Since the rack is not valid in the first place,
        it doesn't matter if the board is valid or not.
        The returned error should still be RACK_NOT_FOUND.
    """
    _, response = app.test_client.get(invalid_board_info_url)

    assert response.status == 500

    data = ujson.loads(response.text)

    assert 'http_code' in data
    assert 'error_id' in data
    assert 'description' in data
    assert 'timestamp' in data
    assert 'context' in data

    assert data['http_code'] == 500
    assert data['error_id'] == errors.RACK_NOT_FOUND


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
    """Test getting a device info response.

    Details:
        In this case, rack, board, device are invalid.
        Since the rack is not valid in the first place,
        it doesn't matter if the board is or device valid or not.
        The returned error should still be RACK_NOT_FOUND.
    """
    _, response = app.test_client.get(invalid_device_info_url)

    assert response.status == 500

    data = ujson.loads(response.text)

    assert 'http_code' in data
    assert 'error_id' in data
    assert 'description' in data
    assert 'timestamp' in data
    assert 'context' in data

    assert data['http_code'] == 500
    assert data['error_id'] == errors.RACK_NOT_FOUND


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
