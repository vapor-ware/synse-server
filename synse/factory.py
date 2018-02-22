"""Factory for creating Synse Server Sanic application instances."""
# pylint: disable=unused-variable,unused-argument

import datetime

from sanic import Sanic
from sanic.exceptions import NotFound, ServerError
from sanic.response import text

from synse import config, errors
from synse.cache import configure_cache
from synse.i18n import init_gettext
from synse.log import logger, setup_logger
from synse.response import json
from synse.routes import aliases, base, core


def make_app():
    """Create a new instance of the Synse Server sanic application.

    This is the means by which all Synse Server applications are created.

    Returns:
        Sanic: A Sanic application setup and configured to serve
            Synse Server routes.
    """
    app = Sanic(__name__, log_config=config.LOGGING)
    app.config.LOGO = None

    config.load()

    setup_logger()
    init_gettext()

    # register the blueprints
    app.blueprint(aliases.bp)
    app.blueprint(base.bp)
    app.blueprint(core.bp)

    _disable_favicon(app)
    _register_error_handling(app)

    configure_cache()

    return app


def _disable_favicon(app):
    """Return empty response when looking for favicon.

    Args:
        app: The Sanic application to add the route to.
    """
    @app.route('/favicon.ico')
    def favicon(*_):
        """Return empty response on favicon request."""
        return text('')


def _register_error_handling(app):
    """Register the 404 and 500 error JSON responses for Synse Server.

    Args:
        app (sanic.Sanic): The Sanic application to add the handling to.
    """

    @app.exception(NotFound)
    def err_404(request, exception):
        """Handler for a 404 error."""
        logger.error('Exception for request: {}'.format(request))
        logger.exception(exception)

        err = {
            'http_code': 404,
            'error_id': errors.URL_NOT_FOUND,
            'description': errors.codes[errors.URL_NOT_FOUND],
            'timestamp': str(datetime.datetime.utcnow()),
            'context': str(exception)
        }

        return json(err, status=404)

    @app.exception(ServerError)
    def err_500(request, exception):
        """Handler for a 500 error."""
        logger.error('Exception for request: {}'.format(request))
        logger.exception(exception)

        if hasattr(exception, 'error_id'):
            error_id = exception.error_id
        else:
            error_id = errors.UNKNOWN

        err = {
            'http_code': 500,
            'error_id': error_id,
            'description': errors.codes[error_id],
            'timestamp': str(datetime.datetime.utcnow()),
            'context': str(exception)
        }

        return json(err, status=500)