"""Factory for creating Synse Server Sanic application instances."""

import shortuuid
import structlog
from sanic import Sanic
from sanic.request import Request
from sanic.response import HTTPResponse
from structlog import contextvars

from synse_server import errors
from synse_server.api import http, websocket

logger = structlog.get_logger()


def new_app() -> Sanic:
    """Create a new instance of the Synse Server Sanic application.

    Returns:
        A Sanic application for Synse Server.
    """

    app = Sanic(
        name='synse-server',
        error_handler=errors.SynseErrorHandler(),
        configure_logging=False,
    )

    # Disable the default Sanic logo.
    app.config.LOGO = None

    # Register the endpoint blueprints with the application.
    app.blueprint(http.core)
    app.blueprint(http.v3)
    app.blueprint(websocket.v3)

    # Add favicon. This will add a favicon, preventing errors being logged when
    # a browser hits an endpoint and can't find the icon.
    app.static('/favicon.ico', '/etc/synse/static/favicon.ico')

    # Register middleware with the application.
    app.register_middleware(on_request, 'request')
    app.register_middleware(on_response, 'response')

    return app


def on_request(request: Request) -> None:
    """Middleware function that runs prior to processing a request via Sanic."""
    # Generate a unique request ID and use it as a field in any logging that
    # takes place during the request handling.
    req_id = shortuuid.uuid()
    request.ctx.uuid = req_id

    contextvars.clear_contextvars()
    contextvars.bind_contextvars(
        request_id=req_id,
    )


def on_response(request: Request, response: HTTPResponse) -> None:
    """Middleware function that runs prior to returning a response via Sanic."""
    # Unbind the request ID from the logger.
    contextvars.unbind_contextvars(
        'request_id',
    )
