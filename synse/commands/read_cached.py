"""Command handler for the `readcached` route."""

import grpc

from synse import cache, errors, plugin
from synse.i18n import _
from synse.log import logger
from synse.scheme import ReadCachedResponse


async def read_cached(start=None, end=None):
    """The handler for the Synse Server "readcached" API command.

    Args:
        start (str): An RFC3339 or RFC3339Nano formatted timestamp
            which defines a starting bound on the cache data to
            return. If no timestamp is specified, there will not
            be a starting bound. (default: None)
        end (str): An RFC3339 or RFC3339Nano formatted timestamp
            which defines an ending bound on the cache data to
            return. If no timestamp is specified, there will not
            be an ending bound. (default: None)

    Yields:
        ReadCachedResponse: The cached reading from the plugin.
    """
    start, end = start or '', end or ''
    logger.debug(_('Read Cached command (start: {}, end: {})').format(start, end))

    # If the plugins have not yet been registered, register them now.
    if len(plugin.Plugin.manager.plugins) == 0:
        logger.debug(_('Re-registering plugins'))
        plugin.register_plugins()

    # For each plugin, we'll want to request a dump of its readings cache.
    async for plugin_name, plugin_handler in plugin.get_plugins():  # pylint: disable=not-an-iterable
        logger.debug(_('Getting readings cache for plugin: {}').format(plugin_name))

        # Get the cached data from the plugin
        try:
            for reading in plugin_handler.client.read_cached(start, end):
                # If there is no reading, we're done iterating
                if reading is None:
                    return

                try:
                    __, device = await cache.get_device_info(  # pylint: disable=unused-variable
                        reading.rack,
                        reading.board,
                        reading.device
                    )
                except errors.DeviceNotFoundError:
                    logger.info(_(
                        'Did not find device {}-{}-{} locally. Skipping device; '
                        'server cache may be out of sync.'
                    ))
                    continue

                yield ReadCachedResponse(
                    device=device,
                    device_reading=reading,
                )

        except grpc.RpcError as ex:
            raise errors.FailedReadCachedCommandError(str(ex)) from ex
