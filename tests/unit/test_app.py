"""Unit tests for the ``synse_server.app`` module."""

from containerlog import contextvars
from sanic.response import HTTPResponse, StreamingHTTPResponse

from synse_server import app, errors


def test_new_app():
    synse_app = app.app

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

    contextvars.bind(
        request_id='test-request',
    )
    ctx = contextvars._CTXVARS
    assert 'test-request' == ctx['containerlog_request_id'].get()

    app.on_response(req, resp)

    ctx = contextvars._CTXVARS
    assert ctx['containerlog_request_id'].get() is Ellipsis


def test_on_response_streaming_http_response():
    class MockRequest:
        method = 'GET'
        url = 'http://localhost'

    req = MockRequest()
    resp = StreamingHTTPResponse(None)

    contextvars.bind(
        request_id='test-request',
    )
    ctx = contextvars._CTXVARS
    assert 'test-request' == ctx['containerlog_request_id'].get()

    app.on_response(req, resp)

    ctx = contextvars._CTXVARS
    assert ctx['containerlog_request_id'].get() is Ellipsis
