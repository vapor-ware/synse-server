"""Test the 'synse.routes.core' Synse Server module's transaction route."""
# pylint: disable=redefined-outer-name,unused-argument

import pytest
import ujson

from synse import factory
from synse.version import __api_version__

invalid_transaction_url = '/synse/{}/transaction/invalid-id'.format(__api_version__)


@pytest.fixture()
def app():
    """Fixture to get a Synse Server application instance."""
    yield factory.make_app()


def test_transaction_endpoint_invalid(app):
    """Test getting a invalid transaction response."""
    _, response = app.test_client.get(invalid_transaction_url)

    assert response.status == 500

    # FIXME: Failed transaction id should return some kind of error message.
    # Right now, it doesn't seem to have one


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
