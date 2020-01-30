
from typing import Any, Dict

from structlog import get_logger
from synse_grpc import utils

from synse_server import cache, errors
from synse_server.i18n import _

logger = get_logger()


async def info(device_id: str) -> Dict[str, Any]:
    """Generate the device info response data.

    Args:
        device_id: The ID of the device to get information for.

    Returns:
        A dictionary representation of the device info response.
    """
    logger.info(_('issuing command'), command='INFO', device_id=device_id)

    device = await cache.get_device(device_id)
    if device is None:
        raise errors.NotFound(f'device not found: {device_id}')

    tags = [utils.tag_string(t) for t in device.tags]
    device_info = utils.to_dict(device)
    device_info['tags'] = tags
    return device_info
