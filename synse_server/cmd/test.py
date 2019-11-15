
from synse_server import utils
from synse_server.i18n import _
from synse_server.log import logger


async def test():
    """Generate the test response data.

    Returns:
        dict: A dictionary representation of the test response.
    """
    logger.info(_('issuing command'), command='TEST')

    return {
        'status': 'ok',
        'timestamp': utils.rfc3339now(),
    }
