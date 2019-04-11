
import synse_server.config
from synse_server.log import logger
from synse_server.i18n import _


async def config():
    """Generate the config response data.

    Returns:
        dict: A dictionary representation of the config response.
    """
    logger.debug(_('issuing command'), command='CONFIG')

    return {k: v for k, v in synse_server.config.options.config.items() if not k.startswith('_')}
