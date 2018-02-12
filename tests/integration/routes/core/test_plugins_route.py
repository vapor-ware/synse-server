"""Test the 'synse.routes.core' Synse Server module's plugin route."""
# pylint: disable=redefined-outer-name,unused-argument

import pytest
import ujson

from synse import factory
from synse.version import __api_version__

plugins_url = '/synse/{}/plugins'.format(__api_version__)


@pytest.fixture()
def app():
    """Fixture to get a Synse Server application instance."""
    yield factory.make_app()


def test_plugins_endpoint_ok(app):
    """Test getting a good plugins response."""
    _, response = app.test_client.get(plugins_url)

    assert response.status == 200

    data = ujson.loads(response.text)

    assert len(data) == 0


def test_plugins_endpoint_post_not_allowed(app):
    """Invalid request: POST"""
    _, response = app.test_client.post(plugins_url)
    assert response.status == 405


def test_plugins_endpoint_put_not_allowed(app):
    """Invalid request: PUT"""
    _, response = app.test_client.put(plugins_url)
    assert response.status == 405


def test_plugins_endpoint_delete_not_allowed(app):
    """Invalid request: DELETE"""
    _, response = app.test_client.delete(plugins_url)
    assert response.status == 405


def test_plugins_endpoint_patch_not_allowed(app):
    """Invalid request: PATCH"""
    _, response = app.test_client.patch(plugins_url)
    assert response.status == 405


def test_plugins_endpoint_head_not_allowed(app):
    """Invalid request: HEAD"""
    _, response = app.test_client.head(plugins_url)
    assert response.status == 405


def test_plugins_endpoint_options_not_allowed(app):
    """Invalid request: OPTIONS"""
    _, response = app.test_client.options(plugins_url)
    assert response.status == 405
