"""Test the 'synse_server.routes.core' module's config route."""
# pylint: disable=redefined-outer-name,unused-argument

import ujson

from synse_server.version import __api_version__

config_url = '/synse/{}/config'.format(__api_version__)

#
# def test_config_endpoint_ok(app):
#     """Get the Synse Server configuration."""
#     _, response = app.test_client.get(config_url)
#     assert response.status == 200
#
#     data = ujson.loads(response.text)
#     assert 'locale' in data
#     assert 'pretty_json' in data
#     assert 'logging' in data
#     assert 'cache' in data
#     assert 'grpc' in data
#
#     assert data['locale'] == 'en_US'
#     assert data['pretty_json'] is True
#     assert data['logging'] == 'info'
#     assert data['cache'] == {'meta': {'ttl': 20}, 'transaction': {'ttl': 300}}
#     assert data['grpc'] == {'timeout': 3}


def test_config_endpoint_post_not_allowed(app):
    """Invalid request: POST"""
    _, response = app.test_client.post(config_url)
    assert response.status == 405


def test_config_endpoint_put_not_allowed(app):
    """Invalid request: PUT"""
    _, response = app.test_client.put(config_url)
    assert response.status == 405


def test_config_endpoint_delete_not_allowed(app):
    """Invalid request: DELETE"""
    _, response = app.test_client.delete(config_url)
    assert response.status == 405


def test_config_endpoint_patch_not_allowed(app):
    """Invalid request: PATCH"""
    _, response = app.test_client.patch(config_url)
    assert response.status == 405


def test_config_endpoint_head_not_allowed(app):
    """Invalid request: HEAD"""
    _, response = app.test_client.head(config_url)
    assert response.status == 405


def test_config_endpoint_options_not_allowed(app):
    """Invalid request: OPTIONS"""
    _, response = app.test_client.options(config_url)
    assert response.status == 405
