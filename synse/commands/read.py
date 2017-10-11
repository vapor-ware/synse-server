"""

"""

import grpc

from synse import errors
from synse.cache import get_metainfo_cache
from synse.log import logger
from synse.proc import get_proc
from synse.scheme import ReadResponse
from synse.utils import get_device_uid


async def read(rack, board, device):
    """

    Args:
        rack (str):
        board (str):
        device (str):
    """

    _uid = await get_device_uid(rack, board, device)
    metainfo = await get_metainfo_cache()
    dev = metainfo.get(_uid)

    if dev is None:
        raise errors.SynseError(
            '{} does not correspond with a known device.'.format(
                '/'.join([rack, board, device]), errors.DEVICE_NOT_FOUND)
        )

    proc = get_proc(dev.protocol)
    if not proc:
        raise errors.SynseError(
            'Unable to find background process named "{}" to read.'.format(
                dev.protocol), errors.PROCESS_NOT_FOUND
        )

    try:
        read_data = [r for r in proc.client.read(_uid)]
    except grpc.RpcError as ex:
        raise errors.SynseError('Failed to issue a read request.', errors.FAILED_READ_COMMAND) from ex

    logger.debug('read results: {}'.format(read_data))
    return ReadResponse(
        device=dev,
        readings=read_data
    )
