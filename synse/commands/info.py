"""Command handler for the `info` route."""

from synse import cache, errors
from synse.i18n import _
from synse.log import logger
from synse.scheme.info import InfoResponse


async def info(rack, board=None, device=None):
    """The handler for the Synse Server "info" API command.

    Args:
        rack (str): The rack to get information for.
        board (str): The board to get information for.
        device (str): The device to get information for.

    Returns:
        InfoResponse: The "info" response scheme model.
    """
    if rack is None:
        raise errors.InvalidArgumentsError(
            _('No rack specified when issuing info command.')
        )

    _cache = await cache.get_resource_info_cache()
    r, b, d = get_resources(_cache, rack, board, device)

    if board is not None:
        if device is not None:
            # we have rack, board, device
            logger.debug('info >> rack, board, device')
            response = d

        else:
            # we have rack, board
            logger.debug('info >> rack, board')
            response = {
                'board': b['board'],
                'location': {'rack': r['rack']},
                'devices': list(b['devices'].keys())
            }

    else:
        # we have rack
        logger.debug('info >> rack')
        response = {
            'rack': r['rack'],
            'boards': list(r['boards'].keys())
        }

    return InfoResponse(response)


def get_resources(info_cache, rack=None, board=None, device=None):
    """Get the entries for the specified resources out of the resource info
    cache.

    If a given resource (rack, board, device) is provided as None, it will not
    be looked up and that resource will have None as its return value.

    If any of the specified resources can not be found in the cache, an error
    is raised.

    Args:
        info_cache (dict): The resource info cache.
        rack (str): The identifier for the rack to get info for.
        board (str): The identifier for the board to get info for.
        device (str): The identifier for the device to get info for.

    Returns:
        tuple: A 3-tuple with the corresponding rack, board, and device
            entry.

    Raises:
        errors.SynseError: Any of the specified resources were not found in
            the resource info cache.
    """
    r, b, d = None, None, None

    if rack is not None:
        r = info_cache.get(rack)
        if not r:
            raise errors.RackNotFoundError(
                _('Unable to find rack "{}" in info cache.').format(rack)
            )

    if board is not None:
        b = r['boards'].get(board)
        if not b:
            raise errors.BoardNotFoundError(
                _('Unable to find board "{}" in info cache.').format(board)
            )

    if device is not None:
        d = b['devices'].get(device)
        if not d:
            raise errors.DeviceNotFoundError(
                _('Unable to find device "{}" in info cache.').format(device)
            )

    return r, b, d
