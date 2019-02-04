"""Command handler for the `capabilities` route."""

from synse_server import cache
from synse_server.i18n import _
from synse_server.log import logger
from synse_server.scheme.capabilities import CapabilitiesResponse


async def capabilities():
    """The handler for the Synse Server "capabilities" API command.

    Returns:
        CapabilitiesResponse: The "capabilities" response scheme model.
    """
    logger.debug(_('Capabilities Command'))

    cache_data = await cache.get_capabilities_cache()
    return CapabilitiesResponse(data=cache_data)
