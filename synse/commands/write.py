"""Command handler for the `write` route.
"""

import grpc

from synse import errors
from synse.cache import add_transaction, get_device_meta
from synse.log import logger
from synse.plugin import get_plugin
from synse.scheme.write import WriteResponse


async def write(rack, board, device, data):
    """

    Args:
        rack (str):
        board (str):
        device (str):
        data ():
    """

    # lookup the known info for the specified device
    dev = await get_device_meta(rack, board, device)

    # get the plugin context for the device's specified protocol
    plugin = get_plugin(dev.protocol)
    if not plugin:
        raise errors.SynseError(
            'Unable to find plugin named "{}" to write to.'.format(
                dev.protocol), errors.PLUGIN_NOT_FOUND
        )

    # perform a gRPC write on the device's managing plugin
    try:
        transaction = plugin.client.write(rack, board, device, [data])
    except grpc.RpcError as ex:
        raise errors.SynseError('Failed to issue a write request.', errors.FAILED_WRITE_COMMAND) from ex

    # now that we have the transaction info, we want to map it to the corresponding
    # process so any subsequent transaction check will know where to look.
    ok = await add_transaction(transaction.id, plugin.name)
    if not ok:
        logger.error('Failed to add transaction {} to the cache.'.format(transaction.id))

    return WriteResponse(
        transaction=transaction
    )
