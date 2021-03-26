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

    logger.debug(
        'processing HTTP request',
        method=request.method,
        ip=request.ip,
        path=request.path,
        headers=dict(request.headers),
        args=request.args,
    )


def on_response(request: Request, response: HTTPResponse) -> None:
    """Middleware function that runs prior to returning a response via Sanic."""

    # Default bytes. If this is a StreamingHTTPResponse, this value is
    # used, since there is no response.body for those responses.
    # (https://github.com/vapor-ware/synse-server/issues/396)
    byte_count = -1
    if hasattr(response, 'body') and response.body is not None:
        byte_count = len(response.body)

    logger.debug(
        'returning HTTP response',
        request=f'{request.method} {request.url}',
        status=response.status,
        bytes=byte_count,
    )

    # Unbind the request ID from the logger.
    contextvars.unbind_contextvars(
        'request_id',
    )



# def new_app(name=None) -> Sanic:
#     """Create a new instance of the Synse Server Sanic application.
#
#     Args:
#         name: Name of the application. This allows tests to create application
#             instances with different names.
#
#     Returns:
#         A Sanic application for Synse Server.
#     """

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

    # return app


