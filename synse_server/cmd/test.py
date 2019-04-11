
from synse_server import utils
from synse_server.log import logger
from synse_server.i18n import _


async def test():
    """Generate the test response data.

    Returns:
        dict: A dictionary representation of the test response.
    """
    logger.debug(_('issuing command'), command='TEST')

    return {
        'status': 'ok',
        'timestamp': utils.rfc3339now(),
    }
