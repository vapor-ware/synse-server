"""Command handler for the `scan` route.
"""

from synse.cache import clear_all_meta_caches, get_scan_cache
from synse.log import logger
from synse.scheme.scan import ScanResponse


async def scan(rack=None, board=None, force=False):
    """

    Args:
        rack (str):
        board (str):
        force (bool):
    """
    if force:
        await clear_all_meta_caches()

    logger.debug('Running "scan" command.')
    cache_data = await get_scan_cache()

    logger.debug('Making "scan" response.')
    return ScanResponse(
        data=cache_data
    )
