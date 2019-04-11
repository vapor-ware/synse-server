
import synse_server
from synse_server.log import logger
from synse_server.i18n import _


async def version():
    """Generate the version response data.

    Returns:
        dict: A dictionary representation of the version response.
    """
    logger.debug(_('issuing command'), command='VERSION')

    return {
        'version': synse_server.__version__,
        'api_version': synse_server.__api_version__,
    }
