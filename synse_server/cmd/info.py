
from synse_grpc import utils

from synse_server import cache, errors
from synse_server.i18n import _
from synse_server.log import logger


async def info(device_id):
    """Generate the device info response data.

    Args:
        device_id (str): The ID of the device to get information for.

    Returns:
        dict: A dictionary representation of the device info response.
    """
    logger.debug(_('issuing command'), command='INFO', device_id=device_id)

    device = await cache.get_device(device_id)
    if device is None:
        raise errors.NotFound(f'device not found: {device_id}')

    tags = [utils.tag_string(t) for t in device.tags]
    device_info = utils.to_dict(device)
    device_info['tags'] = tags
    return device_info
