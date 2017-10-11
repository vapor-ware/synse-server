"""

"""

from synse import errors
from synse.cache import get_resource_info_cache
from synse.log import logger
from synse.scheme.info import InfoResponse


async def info(rack, board=None, device=None):
    """

    Args:
        rack (str):
        board (str):
        device (str):
    """
    if rack is None:
        raise errors.SynseError('No rack specified when issuing info command.', errors.INVALID_ARGUMENTS)

    if board is not None:
        if device is not None:
            # we have rack, board, device
            logger.debug('info >> rack, board, device')
            pass

        else:
            # we have rack, board
            logger.debug('info >> rack, board')
            pass

    else:
        # we have rack
        logger.debug('info >> rack')
        pass

    cache = await get_resource_info_cache()
    return InfoResponse(cache)
