
from typing import Dict

from containerlog import get_logger

from synse_server import utils

logger = get_logger()


async def test() -> Dict[str, str]:
    """Generate the test response data.

    Returns:
        A dictionary representation of the test response.
    """
    logger.info('issuing command', command='TEST')

    return {
        'status': 'ok',
        'timestamp': utils.rfc3339now(),
    }
