"""Command handler for the `read` route.
"""

import grpc

from synse import errors
from synse.cache import get_device_meta
from synse.log import logger
from synse.plugin import get_plugin
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
    logger.debug('>> READ cmd')

    # lookup the known info for the specified device
    dev = await get_device_meta(rack, board, device)
    logger.debug('  |- got device: {}'.format(dev))

    # get the plugin context for the device's specified protocol
    plugin = get_plugin(dev.protocol)
    logger.debug('  |- got plugin: {}'.format(plugin))
    if not plugin:
        raise errors.SynseError(
            'Unable to find plugin named "{}" to read.'.format(
                dev.protocol), errors.PLUGIN_NOT_FOUND
        )

    # perform a gRPC read on the device's managing plugin
    try:
        read_data = [r for r in plugin.client.read(rack, board, device)]
    except grpc.RpcError as ex:
        logger.error('  |- (error): {}'.format(ex))
        raise errors.SynseError(
            'Failed to issue a read request.', errors.FAILED_READ_COMMAND
        ) from ex

    logger.debug('  |- read results: {}'.format(read_data))
    return ReadResponse(
        device=dev,
        readings=read_data
    )
