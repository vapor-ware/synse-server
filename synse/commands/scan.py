"""Command handler for the `scan` route.
"""

from synse import cache, errors, plugin
from synse.log import logger
from synse.scheme.scan import ScanResponse


async def scan(rack=None, board=None, force=False):
    """The handler for the Synse Server "scan" API command.

    Args:
        rack (str): The rack to filter the scan results by.
        board (str): The board to filter the scan results by.
        force (bool): Force a re-scan of the meta-information.

    Returns:
        ScanResponse: The "scan" response scheme model.
    """
    if force:
        await cache.clear_all_meta_caches()

    # plugins are registered on scan. if no plugins exist and a scan is
    # performed (e.g. on startup), we will find and register plugins.
    # additionally, if we are forcing re-scan, we will re-register plugins.
    # this allows us to pick up any dynamically added plugins and clear out
    # any plugins that were removed.
    if len(plugin.Plugin.manager.plugins) == 0 or force:
        logger.debug(gettext('Re-registering plugins.'))
        plugin.register_plugins()

    logger.debug(gettext('Running "scan" command.'))
    cache_data = await cache.get_scan_cache()

    if rack is not None:
        for r in cache_data['racks']:
            if r['rack_id'] == rack:
                cache_data = r
                break
        else:
            raise errors.RackNotFoundError(
                gettext('Rack "{}" not found in scan results.').format(rack)
            )

        if board is not None:
            for b in cache_data['boards']:
                if b['board_id'] == board:
                    cache_data = b
                    break
            else:
                raise errors.BoardNotFoundError(
                    gettext('Board "{}" not found in scan results.').format(board)
                )

    logger.debug(gettext('Making "scan" response.'))
    return ScanResponse(
        data=cache_data
    )
