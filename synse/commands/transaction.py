"""

"""

import grpc

from synse import errors
from synse.cache import get_transaction
from synse.proc import get_proc
from synse.scheme.transaction import TransactionResponse


async def check_transaction(transaction_id):
    """

    Args:
        transaction_id (str):
    """

    proc_name = await get_transaction(transaction_id)
    if not proc_name:
        # TODO - in the future, what we could do is attempt sending the transaction
        #   request to *all* of the known processes. this could be useful in the event
        #   that synse goes down. since everything is just stored in memory, a new
        #   synse instance will have lost the transaction cache.
        #
        #   alternatively, we could think about having an internal api command to
        #   essentially dump the active transactions so that we can rebuild the cache.
        raise errors.SynseError('Unable to determine process for the given transaction.', errors.TRANSACTION_NOT_FOUND)

    proc = get_proc(proc_name)
    if not proc:
        raise errors.SynseError(
            'Unable to find background process named "{}" to read.'.format(
                proc_name), errors.PROCESS_NOT_FOUND
        )

    try:
        status = proc.client.check_transaction(transaction_id)
    except grpc.RpcError as ex:
        raise errors.SynseError('Failed to issue a transaction check request.', errors.FAILED_TRANSACTION_COMMAND) from ex

    return TransactionResponse(status)
