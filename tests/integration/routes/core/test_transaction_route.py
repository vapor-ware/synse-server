"""Test the 'synse_server.routes.core' module's transaction route."""

from synse_server import __api_version__, errors
from tests import utils

invalid_transaction_url = '/synse/{}/transaction/invalid-id'.format(__api_version__)


def test_transaction_endpoint_invalid(app):
    """Test getting a invalid transaction response."""
    _, response = app.test_client.get(invalid_transaction_url)
    utils.test_error_json(response, errors.NotFound, 404)


def test_transaction_endpoint_post_not_allowed(app):
    """Invalid request: POST"""
    _, response = app.test_client.post(invalid_transaction_url)
    assert response.status == 405


def test_transaction_endpoint_put_not_allowed(app):
    """Invalid request: PUT"""
    _, response = app.test_client.put(invalid_transaction_url)
    assert response.status == 405


def test_transaction_endpoint_delete_not_allowed(app):
    """Invalid request: DELETE"""
    _, response = app.test_client.delete(invalid_transaction_url)
    assert response.status == 405


def test_transaction_endpoint_patch_not_allowed(app):
    """Invalid request: PATCH"""
    _, response = app.test_client.patch(invalid_transaction_url)
    assert response.status == 405


def test_transaction_endpoint_head_not_allowed(app):
    """Invalid request: HEAD"""
    _, response = app.test_client.head(invalid_transaction_url)
    assert response.status == 405


def test_transaction_endpoint_options_not_allowed(app):
    """Invalid request: OPTIONS"""
    _, response = app.test_client.options(invalid_transaction_url)
    assert response.status == 405
