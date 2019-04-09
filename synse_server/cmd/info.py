
from synse_server.log import logger
from synse_server.i18n import _


async def info():
    """Generate the device info response data.

    Returns:
        dict: A dictionary representation of the device info response.
    """
    logger.debug(_('issuing command'), command='INFO')
