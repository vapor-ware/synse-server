
from typing import Dict

import synse_server
from synse_server.i18n import _
from synse_server.log import logger


async def version() -> Dict[str, str]:
    """Generate the version response data.

    Returns:
        A dictionary representation of the version response.
    """
    logger.info(_('issuing command'), command='VERSION')

    return {
        'version': synse_server.__version__,
        'api_version': synse_server.__api_version__,
    }
