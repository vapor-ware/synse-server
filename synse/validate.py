"""Synse Server utility and convenience methods.
"""

from synse import cache, errors
from synse.i18n import gettext


async def validate_device_type(device_type, rack, board, device):
    """Validate that the device associated with the given routing info
    (rack, board device) matches the given device type.

    Args:
        device_type (str): The type of the device, e.g. "led", "fan", etc.
        rack (str): The rack which the device belongs to.
        board (str): The board which the device belongs to.
        device (str): The ID of the device.

    Raises:
        SynseError: The device does not match the given type.
        SynseError: The specified device is not found.
    """
    _, device = await cache.get_device_meta(rack, board, device)
    if device.type != device_type.lower():
        raise errors.InvalidDeviceType(
            gettext('Device ({}) is not of type {}').format(device.type, device_type)
        )
