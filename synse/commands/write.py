"""

"""

import grpc

from synse import errors
from synse.cache import add_transaction, get_metainfo_cache
from synse.log import logger
from synse.proc import get_proc
from synse.scheme.write import WriteResponse
from synse.utils import get_device_uid


async def write(rack, board, device, data):
    """

    Args:
        rack (str):
        board (str):
        device (str):
        data ():
    """

    _uid = await get_device_uid(rack, board, device)
    metainfo = await get_metainfo_cache()
    dev = metainfo.get(_uid)

    if dev is None:
        raise errors.SynseError(
            '{} does not correspond with a known device.'.format(
                '/'.join([rack, board, device]), errors.DEVICE_NOT_FOUND)
        )

    # FIXME - since we are only using dev here to get at the protocol, perhaps
    # we should instead just have a uuid->proto lookup table so we dont have to
    # do the extra step of looking up the device itself?
    proc = get_proc(dev.protocol)
    if not proc:
        raise errors.SynseError(
            'Unable to find background process named "{}" to write to.'.format(
                dev.protocol), errors.PROCESS_NOT_FOUND
        )

    try:
        transaction = proc.client.write(_uid, [data])
    except grpc.RpcError as ex:
        raise errors.SynseError('Failed to issue a write request.', errors.FAILED_WRITE_COMMAND) from ex

    # now that we have the transaction info, we want to map it to the corresponding
    # process so any subsequent transaction check will know where to look.
    ok = await add_transaction(transaction.id, proc.name)
    if not ok:
        logger.error('Failed to add transaction {} to the cache.'.format(transaction.id))

    return WriteResponse(
        transaction=transaction
    )
