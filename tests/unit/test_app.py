"""Unit tests for the ``synse_server.app`` module."""

from sanic.response import HTTPResponse, StreamingHTTPResponse
from structlog import contextvars

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


def test_on_response_normal_http_response():
    class MockRequest:
        method = 'GET'
        url = 'http://localhost'

    req = MockRequest()
    resp = HTTPResponse()

    contextvars.bind_contextvars(
        request_id='test-request',
    )
    ctx = contextvars._get_context()
    assert 'test-request' == ctx.get('request_id')

    app.on_response(req, resp)

    ctx = contextvars._get_context()
    assert ctx.get('request_id') is None


def test_on_response_streaming_http_response():
    class MockRequest:
        method = 'GET'
        url = 'http://localhost'

    req = MockRequest()
    resp = StreamingHTTPResponse(None)

    contextvars.bind_contextvars(
        request_id='test-request',
    )
    ctx = contextvars._get_context()
    assert 'test-request' == ctx.get('request_id')

    app.on_response(req, resp)

    ctx = contextvars._get_context()
    assert ctx.get('request_id') is None
