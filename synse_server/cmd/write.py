
from synse_server.log import logger
from synse_server.i18n import _


async def write_async():
    """"""
    logger.debug(_('issuing command'), command='WRITE ASYNC')


async def write_sync():
    """"""
    logger.debug(_('issuing command'), command='WRITE SYNC')


def write():
    """Generate the asynchronous write response data.

    Returns:
         list[dict]: A list of dictionary representations of asynchronous
         write response(s).
    """
    pass
