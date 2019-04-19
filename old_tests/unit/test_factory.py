"""Test the 'synse_server.factory' Synse Server module."""

# import os
#
# import pytest
# import ujson
# import yaml
#
# from synse_server import config, errors, app
#
#
# @pytest.fixture()
# def make_config(tmpdir):
#     """Fixture to make a simple config file in the datadir"""
#     datadir = tmpdir.mkdir('appconfig')
#
#     with open(os.path.join(datadir, 'config.yml'), 'w') as f:
#         yaml.dump({'log': 'debug'}, f)
#
#     return datadir
#
#
# def test_make_app(make_config):
#     """Create a new instance of the Synse Server app."""
#     config.options.set('locale', 'en_US')
#     config.options.add_config_paths(make_config)
#     app = factory.make_app()
#
#     # check that the app we create has the expected blueprints registered
#     assert 'synse_server.routes.core' in app.blueprints
#     assert 'synse_server.routes.base' in app.blueprints
#     assert 'synse_server.routes.aliases' in app.blueprints
#
#
# def test_disable_favicon(app):
#     """Check empty response when looking for favicon"""
#     _, response = app.test_client.get('/favicon.ico')
#
#     assert response.status == 200
#     assert response.text == ''
#
#
# def test_register_error_handling_400(app):
#     """Check registering 404 error JSON response"""
#     _, response = app.test_client.get('/404')
#
#     assert response.status == 404
#
#     data = ujson.loads(response.text)
#
#     assert 'http_code' in data
#     assert 'error_id' in data
#     assert 'description' in data
#     assert 'timestamp' in data
#     assert 'context' in data
#
#     assert data['http_code'] == 404
#     assert data['error_id'] == errors.URL_NOT_FOUND
