"""Factory for creating Synse Server Sanic application instances."""

from sanic import Sanic

from synse_server import errors
from synse_server.api import http, websocket


def new_app():
    """Create a new instance of the Synse Server Sanic application.

    Returns:
        Sanic: A Sanic application for Synse Server.
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

    return app
