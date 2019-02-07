"""Factory for creating Synse Server Sanic application instances."""

from sanic import Sanic
from sanic.response import text

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
    )

    # Disable the default Sanic logo.
    app.config.LOGO = None

    # Register the endpoint blueprints with the application.
    app.blueprint(http.core)
    app.blueprint(http.v3)
    app.blueprint(websocket.v3)

    # Disable favicon
    #
    # Add a route which provides an empty response for '/favicon.ico' in order
    # to prevent missing favicon errors from populating the logs when Synse
    # Server is hit via web browser.
    # TODO (etd): we could add an icon to return here if we wanted.
    app.add_route(lambda *_: text(''), '/favicon.ico')

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
