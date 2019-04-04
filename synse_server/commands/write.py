"""Command handler for the `write` route."""

import grpc

from synse_server import cache, errors, plugin
from synse_server.i18n import _
from synse_server.log import logger
from synse_server.scheme.write import WriteResponse


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
    logger.debug(
        _('Write Command (args: {}, {}, {}, data: {})')
        .format(rack, board, device, data)
    )

    # Lookup the known info for the specified device
    plugin_name, __ = await cache.get_device_info(rack, board, device)

    # Get the plugin context for the device's specified protocol
    _plugin = plugin.get_plugin(plugin_name)
    if not _plugin:
        raise errors.NotFound(
            _('Unable to find plugin named "{}"').format(plugin_name)
        )

    # The data comes in as the POSTed dictionary which includes an 'action'
    # and/or 'raw'/'data' field. Here, we convert it to the appropriate modeling for
    # transport to the plugin.
    write_action = data.get('action')
    if not isinstance(write_action, str):
        raise errors.InvalidUsage(
            _('"action" value must be a string, but was {}').format(type(write_action))
        )

    # Get the data out. If the 'data' field is present, we will use it. Otherwise, we will
    # look for a 'raw' field, for backwards compatibility. If 'data' exists, 'raw' is ignored.
    write_data = data.get('data')
    if write_data is None:
        write_data = data.get('raw')

    if write_data is not None:
        # The data should be an instance of bytes, which in python is a string
        if not isinstance(write_data, str):
            raise errors.InvalidUsage(
                _('"raw"/"data" value must be a string, but was {}').format(type(write_data))
            )
        write_data = str.encode(write_data)

    wd = {'action': write_action, 'data': write_data}
    logger.info(_('Writing to {}: {}').format('/'.join((rack, board, device)), wd))

    # Perform a gRPC write on the device's managing plugin
    try:
        t = _plugin.client.write(rack, board, device, [wd])
    except grpc.RpcError as ex:
        raise errors.ServerError(str(ex)) from ex

    # Now that we have the transaction info, we want to map it to the corresponding
    # process so any subsequent transaction check will know where to look.
    for _id, ctx in t.transactions.items():
        context = {
            'action': ctx.action,
            'data': ctx.data
        }
        ok = await cache.add_transaction(_id, context, _plugin.id())
        if not ok:
            logger.error(_('Failed to add transaction {} to the cache').format(_id))

    return WriteResponse(
        transactions=t.transactions
    )
