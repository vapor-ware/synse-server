"""Factory for creating Synse Server Sanic application instances."""
# pylint: disable=unused-variable,unused-argument

import os

from sanic import Sanic
from sanic.exceptions import InvalidUsage, NotFound, ServerError
from sanic.response import text

import synse
from synse import config, errors, utils
from synse.cache import configure_cache
from synse.log import LOGGING, logger, setup_logger
from synse.response import json
from synse.routes import aliases, base, core


def make_app():
    """Create a new instance of the Synse Server Sanic application.

    This is the means by which all Synse Server applications should
    be created.

    Returns:
        Sanic: A Sanic application setup and configured to serve
            Synse Server routes.
    """
    app = Sanic(__name__, log_config=LOGGING)
    app.config.LOGO = None

    # Get the application configuration(s)
    config.options.add_config_paths('.', '/synse/config')
    config.options.env_prefix = 'SYNSE'
    config.options.auto_env = True

    config.options.parse(requires_cfg=False)
    config.options.validate()

    # Set up application logging
    setup_logger()

    # Set the language environment variable to that set in the config, if
    # it is not already set. This is how we specify the language/locale for
    # the application.
    # FIXME (etd): this isn't a great way of doing things, especially if Synse
    # Server is being run in a non-containerized environment.
    lang = os.environ.get('LANGUAGE')
    if lang:
        logger.info('LANGUAGE set from env: {}'.format(lang))
    else:
        lang = config.options.get('locale')
        logger.info('LANGUAGE set from config: {}'.format(lang))
        os.environ['LANGUAGE'] = lang

    # Register the blueprints
    app.blueprint(aliases.bp)
    app.blueprint(base.bp)
    app.blueprint(core.bp)

    _disable_favicon(app)
    _register_error_handling(app)

    configure_cache()

    # Log out metadata for Synse Server and the application configuration
    logger.info('Synse Server:')
    logger.info('  version: {}'.format(synse.__version__))
    logger.info('  author:  {}'.format(synse.__author__))
    logger.info('  url:     {}'.format(synse.__url__))
    logger.info('  license: {}'.format(synse.__license__))
    logger.info('Configuration: {}'.format(config.options.config))
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
    """Register the 400, 404 and 500 error JSON responses for Synse Server.

    Args:
        app (sanic.Sanic): The Sanic application to add the handling to.
    """

    @app.exception(NotFound)
    def err_404(request, exception):
        """Handler for a 404 error."""
        logger.error('Exception for request: {}'.format(request))
        logger.exception(exception)

        if hasattr(exception, 'error_id'):
            error_id = exception.error_id
        else:
            error_id = errors.URL_NOT_FOUND

        return _make_error(error_id, exception)

    @app.exception(ServerError, InvalidUsage)
    def err(request, exception):
        """Handler for a 500 and 400 error."""
        logger.error('Exception for request: {}'.format(request))
        logger.exception(exception)

        if hasattr(exception, 'error_id'):
            error_id = exception.error_id
        else:
            error_id = errors.UNKNOWN

        return _make_error(error_id, exception)


def _make_error(error_id, exception):
    """Make a JSON error response."""
    error = {
        'http_code': exception.status_code,
        'error_id': error_id,
        'description': errors.codes[error_id],
        'timestamp': utils.rfc3339now(),
        'context': str(exception)

    }
    return json(error, status=exception.status_code)
