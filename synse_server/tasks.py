"""Asynchronous background tasks."""

import asyncio

from synse_server.cache import clear_all_meta_caches
from synse_server.log import logger


def register_with_app(app):
    """Register all tasks with a Sanic application instance.

    Args:
        app (sanic.Sanic): The application to register the tasks with.
    """
    # Periodically invalidate caches
    app.add_task(_periodic_cache_invalidation)


async def _periodic_cache_invalidation():
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
