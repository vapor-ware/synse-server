"""Command handler for the `info` route.
"""

from synse import errors
from synse.cache import get_resource_info_cache
from synse.log import logger
from synse.scheme.info import InfoResponse


async def info(rack, board=None, device=None):
    """The handler for the Synse Server "info" API command.

    Args:
        rack (str): The rack to get information for.
        board (str): The board to get information for.
        device (str): The device to get information for.

    Returns:
        InfoResponse: The "info" response scheme model.
    """
    if rack is None:
        raise errors.SynseError(
            'No rack specified when issuing info command.', errors.INVALID_ARGUMENTS
        )

    if board is not None:
        if device is not None:
            # we have rack, board, device
            logger.debug('info >> rack, board, device')

        else:
            # we have rack, board
            logger.debug('info >> rack, board')

    else:
        # we have rack
        logger.debug('info >> rack')

    cache = await get_resource_info_cache()
    return InfoResponse(cache)
