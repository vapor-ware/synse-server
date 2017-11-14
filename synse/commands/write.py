"""Command handler for the `write` route.
"""

import grpc

from synse import errors
from synse.cache import add_transaction, get_device_meta
from synse.log import logger
from synse.plugin import get_plugin
from synse.proto.client import WriteData
from synse.scheme.write import WriteResponse


async def write(rack, board, device, data):
    """The handler for the Synse Server "write" API command.

    Args:
        rack (str): The rack which the device resides on.
        board (str): The board which the device resides on.
        device (str): The device to write to.
        data (dict): The data to write to the device.

    Returns:
        WriteResponse: The "write" response scheme model.
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

    # the data comes in as the POSTed dictionary which includes an 'action'
    # and/or 'raw' field. here, we convert it to the appropriate modeling for
    # transport to the plugin.
    action = data.get('action')
    raw = data.get('raw')
    if raw is not None:
        # raw will be a string - we need to convert to bytes
        raw = [str.encode(raw)]

    wd = WriteData(action=action, raw=raw)

    # perform a gRPC write on the device's managing plugin
    try:
        t = plugin.client.write(rack, board, device, [wd])
    except grpc.RpcError as ex:
        raise errors.SynseError(
            'Failed to issue a write request.', errors.FAILED_WRITE_COMMAND
        ) from ex

    # now that we have the transaction info, we want to map it to the corresponding
    # process so any subsequent transaction check will know where to look.
    for _id, ctx in t.transactions.items():
        context = {
            'action': ctx.action,
            'raw': ctx.raw
        }
        ok = await add_transaction(_id, context, plugin.name)
        if not ok:
            logger.error('Failed to add transaction {} to the cache.'.format(_id))

    return WriteResponse(
        transactions=t.transactions
    )
