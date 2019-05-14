"""Asynchronous background tasks."""

import asyncio

from synse_server import config
from synse_server.cache import update_device_cache
from synse_server.i18n import _
from synse_server.log import logger


def register_with_app(app):
    """Register all tasks with a Sanic application instance.

    Args:
        app (sanic.Sanic): The application to register the tasks with.
    """
    # Periodically invalidate caches
    logger.info(_('adding task'), task='periodic device cache rebuild')
    app.add_task(_rebuild_device_cache)


async def _rebuild_device_cache():
    """Periodically rebuild the device cache."""
    interval = config.options.get('cache.device.rebuild_every', 3 * 60)  # 3 minute default

    while True:
        logger.info(
            _('rebuilding device cache'),
            task='periodic cache rebuild', interval=interval,
        )

        try:
            await update_device_cache()
        except Exception as e:
            logger.error(
                _('failed to rebuild device cache'),
                task='periodic cache rebuild', interval=interval, error=e,
            )

        await asyncio.sleep(interval)
