"""Command handler for the `scan` route."""

from synse_server import cache, errors, plugin
from synse_server.i18n import _
from synse_server.log import logger
from synse_server.scheme.scan import ScanResponse


async def scan(rack=None, board=None, force=False):
    """The handler for the Synse Server "scan" API command.

    Args:
        rack (str): The rack to filter the scan results by.
        board (str): The board to filter the scan results by.
        force (bool): Force a re-scan of the meta-information.

    Returns:
        ScanResponse: The "scan" response scheme model.
    """
    logger.debug(_('Scan Command (args: {}, {}, force: {})').format(rack, board, force))

    if force:
        await cache.clear_all_meta_caches()

    # Plugins are registered on scan. If no plugins exist and a scan is
    # performed (e.g. on startup), we will find and register plugins.
    # Additionally, if we are forcing re-scan, we will re-register plugins.
    # This allows us to pick up any dynamically added plugins and clear out
    # any plugins that were removed.
    if len(plugin.Plugin.manager.plugins) == 0 or force:
        logger.debug(_('Re-registering plugins'))
        plugin.register_plugins()

    cache_data = await cache.get_scan_cache()

    # Filter the scan results by rack.
    if rack is not None:
        if not cache_data:
            raise errors.FailedScanCommandError(
                _('Unable to filter by resource - no scan results returned')
            )

        for r in cache_data['racks']:
            if r['id'] == rack:
                cache_data = r
                break
        else:
            raise errors.RackNotFoundError(
                _('Rack "{}" not found in scan results').format(rack)
            )

        # Filter the rack results by board.
        if board is not None:
            for b in cache_data['boards']:
                if b['id'] == board:
                    cache_data = b
                    break
            else:
                raise errors.BoardNotFoundError(
                    _('Board "{}" not found in scan results').format(board)
                )

    return ScanResponse(
        data=cache_data
    )
