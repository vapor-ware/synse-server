"""Test the 'synse_server.routes.core' module's scan route."""

import ujson

from synse_server import errors
from synse_server import __api_version__
from tests import utils

scan_url = '/synse/{}/scan'.format(__api_version__)
invalid_rack_scan_url = '{}/invalid-rack'.format(scan_url)
invalid_board_scan_url = '{}/invalid-board'.format(invalid_rack_scan_url)


def test_scan_endpoint_ok(app):
    """Test getting a scan response.

    Since the emulator plugin is not enabled, there should not
    be any data for the rack.
    """
    _, response = app.test_client.get(scan_url)
    assert response.status == 200

    data = ujson.loads(response.text)
    assert data == {}


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

    There is no plugin backend, so the scan will be empty. When
    the scan is empty, we can't filter on racks/boards.
    """
    _, response = app.test_client.get(invalid_rack_scan_url)
    utils.test_error_json(response, errors.ServerError)


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

    There is no plugin backend, so the scan will be empty. When
    the scan is empty, we can't filter on racks/boards.
    """
    _, response = app.test_client.get(invalid_board_scan_url)
    utils.test_error_json(response, errors.ServerError)


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
