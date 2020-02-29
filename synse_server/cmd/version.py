
from typing import Dict

from structlog import get_logger

import synse_server

logger = get_logger()


async def version() -> Dict[str, str]:
    """Generate the version response data.

    Returns:
        A dictionary representation of the version response.
    """
    logger.info('issuing command', command='VERSION')

    return {
        'version': synse_server.__version__,
        'api_version': synse_server.__api_version__,
    }
