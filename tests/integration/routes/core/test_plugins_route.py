"""Test the 'synse_server.routes.core' module's plugin route."""
# pylint: disable=redefined-outer-name,unused-argument

import ujson

from synse_server.version import __api_version__

plugins_url = '/synse/{}/plugins'.format(__api_version__)


def test_plugins_endpoint_ok(app):
    """Test getting a good plugins response."""
    _, response = app.test_client.get(plugins_url)
    assert response.status == 200

    # since there is no plugin backend, we don't expect any plugins
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
