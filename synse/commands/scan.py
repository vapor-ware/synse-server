"""Command handler for the `scan` route.
"""

from synse.cache import clear_all_meta_caches, get_scan_cache
from synse.log import logger
from synse.plugin import Plugin, register_plugins
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
        await clear_all_meta_caches()

    # plugins are registered on scan. if no plugins exist and a scan is
    # performed (e.g. on startup), we will find and register plugins.
    # additionally, if we are forcing re-scan, we will re-register plugins.
    # this allows us to pick up any dynamically added plugins and clear out
    # any plugins that were removed.
    if len(Plugin.manager.plugins) == 0 or force:
        register_plugins()

    logger.debug('Running "scan" command.')
    cache_data = await get_scan_cache()

    logger.debug('Making "scan" response.')
    return ScanResponse(
        data=cache_data
    )
