
from typing import Any, Dict

from containerlog import get_logger

from synse_server.config import options

logger = get_logger()


async def config() -> Dict[str, Any]:
    """Generate the config response data.

    Returns:
        A dictionary representation of the config response.
    """
    logger.info('issuing command', command='CONFIG')

    return {k: v for k, v in options.config.items() if not k.startswith('_')}
