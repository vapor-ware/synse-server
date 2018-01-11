"""Command handler for the `read` route.
"""

import grpc

from synse import cache, errors, plugin
from synse.log import logger
from synse.scheme import ReadResponse


async def read(rack, board, device):
    """The handler for the Synse Server "read" API command.

    Args:
        rack (str): The rack which the device resides on.
        board (str): The board which the device resides on.
        device (str): The device to read.

    Returns:
        ReadResponse: The "read" response scheme model.
    """
    logger.debug(gettext('>> READ cmd'))

    # lookup the known info for the specified device
    dev = await cache.get_device_meta(rack, board, device)
    logger.debug(gettext('  |- got device: {}').format(dev))

    # get the plugin context for the device's specified protocol
    _plugin = plugin.get_plugin(dev.protocol)
    logger.debug(gettext('  |- got plugin: {}').format(_plugin))
    if not _plugin:
        raise errors.SynseError(
            gettext('Unable to find plugin named "{}" to read.').format(
                dev.protocol), errors.PLUGIN_NOT_FOUND
        )

    # perform a gRPC read on the device's managing plugin
    try:
        read_data = [r for r in _plugin.client.read(rack, board, device)]
    except grpc.RpcError as ex:
        logger.error(gettext('  |- (error): {}').format(ex))
        raise errors.SynseError(
            gettext('Failed to issue a read request.'), errors.FAILED_READ_COMMAND
        ) from ex

    logger.debug(gettext('  |- read results: {}').format(read_data))
    return ReadResponse(
        device=dev,
        readings=read_data
    )
