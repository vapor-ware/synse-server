
from synse_server import app, errors


def test_new_app():
    synse_app = app.new_app()

    assert synse_app.name == 'synse-server'
    assert isinstance(synse_app.error_handler, errors.SynseErrorHandler)
    assert synse_app.configure_logging is False
    assert synse_app.websocket_enabled is True
    assert synse_app.is_running is False
    assert 'core-http' in synse_app.blueprints
    assert 'v3-http' in synse_app.blueprints
    assert 'v3-websocket' in synse_app.blueprints
