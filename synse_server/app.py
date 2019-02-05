"""Factory for creating Synse Server Sanic application instances."""
# pylint: disable=unused-variable,unused-argument

import asyncio

from sanic import Sanic
from sanic.response import text

from synse_server import errors
from synse_server.cache import clear_all_meta_caches, configure_cache
from synse_server.log import logger, setup_logger
from synse_server.routes import aliases, base, core


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
    app.blueprint(aliases.bp)
    app.blueprint(base.bp)
    app.blueprint(core.bp)

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

    # FIXME (etd): this probably belongs in the Synse class
    setup_logger()
    configure_cache()

    # Add background tasks
    app.add_task(periodic_cache_invalidation)

    return app


async def periodic_cache_invalidation():
    """Periodically invalidate the caches so they are rebuilt."""
    interval = 3 * 60  # 3 minutes

    while True:
        await asyncio.sleep(interval)
        logger.info('task [periodic cache invalidation]: Clearing device caches')

        try:
            await clear_all_meta_caches()
        except Exception as e:
            logger.error(
                'task [periodic cache invalidation]: Failed to clear device caches, '
                'will try again in {}s: {}'
                .format(interval, e)
            )
