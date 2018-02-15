"""Test the 'synse.factory' Synse Server module."""
# pylint: disable=redefined-outer-name,unused-argument

import pytest
import ujson

from synse import config, errors, factory


@pytest.fixture()
def app():
    """Fixture to get a Synse Server application instance."""
    yield factory.make_app()


def test_make_app():
    """Create a new instance of the Synse Server app."""
    config.options['locale'] = 'en_US'
    app = factory.make_app()

    # check that the app we create has the expected blueprints registered
    assert 'synse.routes.core' in app.blueprints
    assert 'synse.routes.base' in app.blueprints
    assert 'synse.routes.aliases' in app.blueprints


def test_disable_favicon(app):
    """Check empty response when looking for favicon"""
    _, response = app.test_client.get('/favicon.ico')

    assert response.status == 200
    assert response.text == ''


def test_register_error_handling_400(app):
    """Check registering 404 error JSON response"""
    _, response = app.test_client.get('/404')

    assert response.status == 404

    data = ujson.loads(response.text)

    assert 'http_code' in data
    assert 'error_id' in data
    assert 'description' in data
    assert 'timestamp' in data
    assert 'context' in data

    assert data['http_code'] == 404
    assert data['error_id'] == errors.URL_NOT_FOUND
