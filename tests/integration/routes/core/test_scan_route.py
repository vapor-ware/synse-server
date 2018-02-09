"""Test the 'synse.routes.core' Synse Server module's scan route."""
# pylint: disable=redefined-outer-name,unused-argument

import pytest
import ujson

from synse import errors, factory
from synse.version import __api_version__

scan_url = '/synse/{}/scan'.format(__api_version__)
invalid_rack_scan_url = '{}/invalid-rack'.format(scan_url)
invalid_board_scan_url = '{}/invalid-board'.format(invalid_rack_scan_url)


@pytest.fixture()
def app():
    """Fixture to get a Synse Server application instance."""
    yield factory.make_app()


def test_scan_endpoint_ok(app):
    """Test getting a scan response.

    Details:
        Since the emulator plugin is not enabled,
        there should not be any data for the rack.
    """
    _, response = app.test_client.get(scan_url)

    assert response.status == 200

    data = ujson.loads(response.text)

    assert 'racks' in data

    assert len(data['racks']) == 0


def test_scan_endpoint_post_not_allowed(app):
    """Invalid request: POST"""
    _, response = app.test_client.post(scan_url)
    assert response.status == 405


def test_scan_endpoint_put_not_allowed(app):
    """Invalid request: PUT"""
    _, response = app.test_client.put(scan_url)
    assert response.status == 405


def test_scan_endpoint_delete_not_allowed(app):
    """Invalid request: DELETE"""
    _, response = app.test_client.delete(scan_url)
    assert response.status == 405


def test_scan_endpoint_patch_not_allowed(app):
    """Invalid request: PATCH"""
    _, response = app.test_client.patch(scan_url)
    assert response.status == 405


def test_scan_endpoint_head_not_allowed(app):
    """Invalid request: HEAD"""
    _, response = app.test_client.head(scan_url)
    assert response.status == 405


def test_scan_endpoint_options_not_allowed(app):
    """Invalid request: OPTIONS"""
    _, response = app.test_client.options(scan_url)
    assert response.status == 405


def test_rack_scan_endpoint_invalid(app):
    """Test getting a invalid rack scan response.

    Details:
        In this case, rack is invalid.
        The returned error should be RACK_NOT_FOUND.
    """
    _, response = app.test_client.get(invalid_rack_scan_url)

    assert response.status == 500

    data = ujson.loads(response.text)

    assert 'http_code' in data
    assert 'error_id' in data
    assert 'description' in data
    assert 'timestamp' in data
    assert 'context' in data

    assert data['http_code'] == 500
    assert data['error_id'] == errors.RACK_NOT_FOUND


def test_rack_scan_endpoint_post_not_allowed(app):
    """Invalid request: POST"""
    _, response = app.test_client.post(invalid_rack_scan_url)
    assert response.status == 405


def test_rack_scan_endpoint_put_not_allowed(app):
    """Invalid request: PUT"""
    _, response = app.test_client.put(invalid_rack_scan_url)
    assert response.status == 405


def test_rack_scan_endpoint_delete_not_allowed(app):
    """Invalid request: DELETE"""
    _, response = app.test_client.delete(invalid_rack_scan_url)
    assert response.status == 405


def test_rack_scan_endpoint_patch_not_allowed(app):
    """Invalid request: PATCH"""
    _, response = app.test_client.patch(invalid_rack_scan_url)
    assert response.status == 405


def test_rack_scan_endpoint_head_not_allowed(app):
    """Invalid request: HEAD"""
    _, response = app.test_client.head(invalid_rack_scan_url)
    assert response.status == 405


def test_rack_scan_endpoint_options_not_allowed(app):
    """Invalid request: OPTIONS"""
    _, response = app.test_client.options(invalid_rack_scan_url)
    assert response.status == 405


def test_board_scan_endpoint_invalid(app):
    """Test getting a board scan response.

    Details:
        In this case, rack and board are invalid.
        Since the rack is not valid in the first place,
        it doesn't matter if the board is valid or not.
        The returned error should still be RACK_NOT_FOUND.
    """
    _, response = app.test_client.get(invalid_board_scan_url)

    assert response.status == 500

    data = ujson.loads(response.text)

    assert 'http_code' in data
    assert 'error_id' in data
    assert 'description' in data
    assert 'timestamp' in data
    assert 'context' in data

    assert data['http_code'] == 500
    assert data['error_id'] == errors.RACK_NOT_FOUND


def test_board_scan_endpoint_post_not_allowed(app):
    """Invalid request: POST"""
    _, response = app.test_client.post(invalid_board_scan_url)
    assert response.status == 405


def test_board_scan_endpoint_put_not_allowed(app):
    """Invalid request: PUT"""
    _, response = app.test_client.put(invalid_board_scan_url)
    assert response.status == 405


def test_board_scan_endpoint_delete_not_allowed(app):
    """Invalid request: DELETE"""
    _, response = app.test_client.delete(invalid_board_scan_url)
    assert response.status == 405


def test_board_scan_endpoint_patch_not_allowed(app):
    """Invalid request: PATCH"""
    _, response = app.test_client.patch(invalid_board_scan_url)
    assert response.status == 405


def test_board_scan_endpoint_head_not_allowed(app):
    """Invalid request: HEAD"""
    _, response = app.test_client.head(invalid_board_scan_url)
    assert response.status == 405


def test_board_scan_endpoint_options_not_allowed(app):
    """Invalid request: OPTIONS"""
    _, response = app.test_client.options(invalid_board_scan_url)
    assert response.status == 405
