"""Factory for creating Synse Server Sanic application instances.
"""

from sanic import Sanic

from synse.log import logger, setup_logger
from synse.routes import aliases, base, core
from synse.utils import (configure_cache, disable_favicon,
                         register_background_plugins,
                         register_error_handling)


def make_app():
    """Create a new instance of the Synse Server sanic application.

    This is the means by which all Synse Server applications are created.

    Returns:
        Sanic: a Sanic application setup and configured to serve
            Synse Server routes.
    """
    app = Sanic(__name__)
    app.config.LOGO = None

    setup_logger()

    # make sure our logger is enabled
    logger.disabled = False

    # register the blueprints
    app.blueprint(aliases.bp)
    app.blueprint(base.bp)
    app.blueprint(core.bp)

    disable_favicon(app)
    register_error_handling(app)

    configure_cache()

    setattr(app, 'register_background_plugins', register_background_plugins)

    return app
