"""Command handler for the `write` route.
"""

import grpc

from synse import cache, errors, plugin
from synse.i18n import gettext
from synse.log import logger
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
    plugin_name, _ = await cache.get_device_meta(rack, board, device)

    # get the plugin context for the device's specified protocol
    _plugin = plugin.get_plugin(plugin_name)
    if not _plugin:
        raise errors.PluginNotFoundError(
            gettext('Unable to find plugin named "{}"').format(plugin_name)
        )

    # the data comes in as the POSTed dictionary which includes an 'action'
    # and/or 'raw' field. here, we convert it to the appropriate modeling for
    # transport to the plugin.
    action = data.get('action')
    if not isinstance(action, str):
        raise errors.InvalidArgumentsError(
            gettext('"action" value must be a string, but was {}'.format(type(action)))
        )

    raw = data.get('raw')
    if raw is not None:
        # raw should be a string - we need to convert to bytes
        if not isinstance(raw, str):
            raise errors.InvalidArgumentsError(
                gettext('"raw" value must be a string, but was {}'.format(type(raw)))
            )
        raw = [str.encode(raw)]

    wd = WriteData(action=action, raw=raw)

    # perform a gRPC write on the device's managing plugin
    try:
        t = _plugin.client.write(rack, board, device, [wd])
    except grpc.RpcError as ex:
        raise errors.FailedWriteCommandError(str(ex)) from ex

    # now that we have the transaction info, we want to map it to the corresponding
    # process so any subsequent transaction check will know where to look.
    for _id, ctx in t.transactions.items():
        context = {
            'action': ctx.action,
            'raw': ctx.raw
        }
        ok = await cache.add_transaction(_id, context, _plugin.name)
        if not ok:
            logger.error(gettext('Failed to add transaction {} to the cache.').format(_id))

    return WriteResponse(
        transactions=t.transactions
    )
