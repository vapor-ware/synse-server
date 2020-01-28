"""Asynchronous background tasks."""

import asyncio

import sanic

from synse_server import config, plugin
from synse_server.cache import update_device_cache
from synse_server.i18n import _
from synse_server.log import logger


def register_with_app(app: sanic.Sanic) -> None:
    """Register all tasks with a Sanic application instance.

    Args:
        app: The application to register the tasks with.
    """
    # Periodically invalidate caches
    logger.info(_('adding task'), task='periodic device cache rebuild')
    app.add_task(_rebuild_device_cache)
    logger.info(_('adding task'), task='periodic plugin refresh')
    app.add_task(_refresh_plugins)


async def _rebuild_device_cache() -> None:
    """Periodically rebuild the device cache."""
    interval = config.options.get('cache.device.rebuild_every', 3 * 60)  # 3 minute default

    while True:
        logger.info(
            _('task: rebuilding device cache'),
            task='periodic cache rebuild', interval=interval,
        )

        try:
            await update_device_cache()
        except Exception as e:
            logger.error(
                _('task: failed to rebuild device cache'),
                task='periodic cache rebuild', interval=interval, error=e,
            )

        await asyncio.sleep(interval)


async def _refresh_plugins() -> None:
    """Periodically refresh the plugin manager."""
    interval = 2 * 60  # 2 minutes

    while True:
        logger.info(
            _('task: refreshing plugins'),
            task='periodic plugin refresh', interval=interval,
        )

        try:
            plugin.manager.refresh()
        except Exception as e:
            logger.error(
                _('task: failed to refresh plugins'),
                task='periodic plugin refresh', interval=interval, error=e,
            )

        await asyncio.sleep(interval)
