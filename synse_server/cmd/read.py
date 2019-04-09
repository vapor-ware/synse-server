
from synse_server.log import logger
from synse_server.i18n import _


async def read():
    """"""
    logger.debug(_('issuing command'), command='READ')


async def read_device():
    """"""
    logger.debug(_('issuing command'), command='READ DEVICE')


async def read_cache():
    """"""
    logger.debug(_('issuing command'), command='READ CACHE')


def readings():
    """Generate the readings response data.

    Returns:
        list[dict]: A list of dictionary representations of device reading
        response(s).
    """
    pass
