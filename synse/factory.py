"""

"""

from sanic import Sanic

from synse.log import logger, setup_logger
from synse.routes.synse import bp
from synse.utils import (configure_cache, disable_favicon,
                         register_background_processes,
                         register_error_handling)


def make_app():
    """
    """
    app = Sanic(__name__)
    app.config.LOGO = None

    setup_logger()

    # make sure our logger is enabled
    logger.disabled = False

    app.blueprint(bp)

    disable_favicon(app)
    register_error_handling(app)

    configure_cache()

    setattr(app, 'register_background_processes', register_background_processes)

    return app
