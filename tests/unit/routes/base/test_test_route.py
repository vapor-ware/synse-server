"""Test the 'synse.routes.base' Synse Server module's test route.
"""
# pylint: disable=redefined-outer-name,unused-argument

import pytest
import ujson

from synse import factory


@pytest.fixture()
def app():
    """Fixture to get a Synse Server application instance."""
    yield factory.make_app()


def test_test_endpoint_ok(app):
    """Test getting a good test response."""
    _, response = app.test_client.get('/synse/test')

    assert response.status == 200

    data = ujson.loads(response.text)

    assert 'status' in data
    assert 'timestamp' in data

    assert data['status'] == 'ok'


def test_test_endpoint_post_not_allowed(app):
    """Invalid request: POST"""
    _, response = app.test_client.post('/synse/test')
    assert response.status == 405


def test_test_endpoint_put_not_allowed(app):
    """Invalid request: PUT"""
    _, response = app.test_client.put('/synse/test')
    assert response.status == 405


def test_test_endpoint_delete_not_allowed(app):
    """Invalid request: DELETE"""
    _, response = app.test_client.delete('/synse/test')
    assert response.status == 405


def test_test_endpoint_patch_not_allowed(app):
    """Invalid request: PATCH"""
    _, response = app.test_client.patch('/synse/test')
    assert response.status == 405


def test_test_endpoint_head_not_allowed(app):
    """Invalid request: HEAD"""
    _, response = app.test_client.head('/synse/test')
    assert response.status == 405


def test_test_endpoint_options_not_allowed(app):
    """Invalid request: OPTIONS"""
    _, response = app.test_client.options('/synse/test')
    assert response.status == 405
