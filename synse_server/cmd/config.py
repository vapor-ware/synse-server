
from typing import Any, Dict

from structlog import get_logger

from synse_server.config import options
from synse_server.i18n import _

logger = get_logger()


async def config() -> Dict[str, Any]:
    """Generate the config response data.

    Returns:
        A dictionary representation of the config response.
    """
    logger.info(_('issuing command'), command='CONFIG')

    return {k: v for k, v in options.config.items() if not k.startswith('_')}
