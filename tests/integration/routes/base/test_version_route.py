"""Test the 'synse.routes.base' Synse Server module's version route."""
# pylint: disable=redefined-outer-name,unused-argument

import pytest
import ujson

from synse import factory, version

version_url = '/synse/version'


@pytest.fixture()
def app():
    """Fixture to get a Synse Server application instance."""
    yield factory.make_app()


def test_version_endpoint_ok(app):
    """Test getting a good version response."""
    _, response = app.test_client.get(version_url)

    assert response.status == 200

    data = ujson.loads(response.text)

    assert 'version' in data
    assert 'api_version' in data

    assert data['version'] == version.__version__
    assert data['api_version'] == version.__api_version__


def test_version_endpoint_post_not_allowed(app):
    """Invalid request: POST"""
    _, response = app.test_client.post(version_url)
    assert response.status == 405


def test_version_endpoint_put_not_allowed(app):
    """Invalid request: PUT"""
    _, response = app.test_client.put(version_url)
    assert response.status == 405


def test_version_endpoint_delete_not_allowed(app):
    """Invalid request: DELETE"""
    _, response = app.test_client.delete(version_url)
    assert response.status == 405


def test_version_endpoint_patch_not_allowed(app):
    """Invalid request: PATCH"""
    _, response = app.test_client.patch(version_url)
    assert response.status == 405


def test_version_endpoint_head_not_allowed(app):
    """Invalid request: HEAD"""
    _, response = app.test_client.head(version_url)
    assert response.status == 405


def test_version_endpoint_options_not_allowed(app):
    """Invalid request: OPTIONS"""
    _, response = app.test_client.options(version_url)
    assert response.status == 405
