"""Command handler for the `scan` route."""

from synse import cache, errors, plugin
from synse.i18n import _
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
        logger.debug(_('Re-registering plugins.'))
        plugin.register_plugins()

    logger.debug(_('Running "scan" command.'))
    cache_data = await cache.get_scan_cache()

    if rack is not None:
        if not cache_data:
            raise errors.FailedScanCommandError(
                _('Unable to filter by resource - no scan results returned.')
            )

        for r in cache_data['racks']:
            if r['id'] == rack:
                cache_data = r
                break
        else:
            raise errors.RackNotFoundError(
                _('Rack "{}" not found in scan results.').format(rack)
            )

        if board is not None:
            for b in cache_data['boards']:
                if b['id'] == board:
                    cache_data = b
                    break
            else:
                raise errors.BoardNotFoundError(
                    _('Board "{}" not found in scan results.').format(board)
                )

    logger.debug(_('Making "scan" response.'))
    return ScanResponse(
        data=cache_data
    )
