"""Command handler for the `read` route."""
# pylint: disable=line-too-long

import grpc
from synse_plugin import api

from synse import cache, errors, plugin, utils
from synse.i18n import _
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
    logger.debug(_('Read Command (args: {}, {}, {})').format(rack, board, device))

    # Lookup the known info for the specified device.
    plugin_name, dev = await cache.get_device_meta(rack, board, device)
    logger.debug(_('Device {} is managed by plugin {}').format(device, plugin_name))

    # Get the plugin context for the device's specified protocol.
    _plugin = plugin.get_plugin(plugin_name)
    logger.debug(_('Got plugin: {}').format(_plugin))
    if not _plugin:
        raise errors.PluginNotFoundError(
            _('Unable to find plugin named "{}" to read').format(plugin_name)
        )

    read_data = []
    try:
        # Perform a gRPC read on the device's managing plugin
        read_data = _plugin.client.read(rack, board, device)
    except grpc.RpcError as ex:

        # FIXME (etd) - this isn't the nicest way of doing this check.
        # this string is returned from the SDK, and its not likely to change
        # anytime soon, so this is "safe" for now, but we should see if there
        # is a better way to check this other than comparing strings..
        if hasattr(ex, 'code') and hasattr(ex, 'details'):
            if grpc.StatusCode.NOT_FOUND == ex.code() and 'no readings found' in ex.details().lower():

                # Currently, in the SDK, there are three different behaviors for
                # devices that do not have readings. Either (a). "null" is returned,
                # (b). an empty string ("") is returned, or (c). a gRPC error is
                # returned with the NOT_FOUND status code. Cases (a) and (b) are
                # handled in the ReadResponse initialization (below). This block
                # handles case (c).
                #
                # The reason for the difference between (a) and (b) is just one
                # of implementation. The empty string is the default value for the
                # gRPC read response, but sometimes it is useful to have an explict
                # value set to make things easier to read.
                #
                # The difference between those and (c) is more distinct. (c) should
                # only happen when a configured device is not being read from at all.
                # Essentially, (c) is the fallback for when device-specific handlers
                # fail to read a configured device.
                #
                # To summarize:
                #   (a), (b)
                #       A device is configured and the plugin's device handlers
                #       can operate on the device. This indicates that the plugin
                #       is working, but the device could be failing or disconnected.
                #
                #   (c)
                #       A device is configured, but the plugin's device handler
                #       can not (or is not) able to operate on the device. This
                #       could indicate either a plugin configuration error or
                #       an error with the plugin logic itself.

                # Create empty readings for each of the device's readings.
                logger.warning(
                    _('Read for {}/{}/{} returned gRPC "no readings found". Will '
                      'apply None as reading value. Note that this response might '
                      'indicate plugin error/misconfiguration.').format(rack, board, device)
                )
                read_data = []
                for output in dev.output:
                    read_data.append(
                        api.ReadResponse(
                            timestamp=utils.rfc3339now(),
                            type=output.type,
                            value='',
                        )
                    )
        else:
            raise errors.FailedReadCommandError(str(ex)) from ex

    return ReadResponse(
        device=dev,
        readings=read_data
    )
