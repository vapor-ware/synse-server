"""Synse Server "read" command.
"""

import grpc

from synse import errors
from synse.cache import get_metainfo_cache
from synse.log import logger
from synse.plugin import get_plugin
from synse.scheme import ReadResponse
from synse.utils import get_device_uid


async def read(rack, board, device):
    """The handler for the Synse Server "read" API command.

    Args:
        rack (str):
        board (str):
        device (str):
    """

    # lookup the known info for the specified device
    # TODO - this can become a helper. used also in 'write' command.
    _uid = await get_device_uid(rack, board, device)
    metainfo = await get_metainfo_cache()
    dev = metainfo.get(_uid)

    if dev is None:
        raise errors.SynseError(
            '{} does not correspond with a known device.'.format(
                '/'.join([rack, board, device]), errors.DEVICE_NOT_FOUND)
        )

    # get the plugin context for the device's specified protocol
    plugin = get_plugin(dev.protocol)
    if not plugin:
        raise errors.SynseError(
            'Unable to find plugin named "{}" to read.'.format(
                dev.protocol), errors.PLUGIN_NOT_FOUND
        )

    # perform a gRPC read on the device's managing plugin
    try:
        read_data = [r for r in plugin.client.read(_uid)]
    except grpc.RpcError as ex:
        raise errors.SynseError('Failed to issue a read request.', errors.FAILED_READ_COMMAND) from ex

    logger.debug('read results: {}'.format(read_data))
    return ReadResponse(
        device=dev,
        readings=read_data
    )
