"""Factory for creating Synse Server Sanic application instances."""

from sanic import Sanic

from synse_server import errors, tasks
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

    # Set the language environment variable to that set in the config, if
    # it is not already set. This is how we specify the language/locale for
    # the application.
    # FIXME (etd): this isn't a great way of doing things, especially if Synse
    # Server is being run in a non-containerized environment.
    # lang = os.environ.get('LANGUAGE')
    # if lang:
    #     logger.info('LANGUAGE set from env: {}'.format(lang))
    # else:
    #     lang = config.options.get('locale')
    #     logger.info('LANGUAGE set from config: {}'.format(lang))
    #     os.environ['LANGUAGE'] = lang

    # Add background tasks
    tasks.register_with_app(app)

    return app
