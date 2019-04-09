
import grpc
import synse_grpc.utils

from synse_server import cache, plugin

from synse_server.log import logger
from synse_server.i18n import _


async def transaction(transaction_id):
    """Generate the transaction response data.

    Args:
        transaction_id (str): The ID of the transaction to get the status of.

    Returns:
         dict: A dictionary representation of the transaction status response.
    """
    logger.debug(_('issuing command'), command='TRANSACTION')

    txn = await cache.get_transaction(transaction_id)
    if not txn:
        # FIXME: raise proper error
        raise ValueError

    plugin_id = txn.get('plugin')
    device = txn.get('device')

    if not plugin_id:
        # FIXME: raise proper error
        raise ValueError

    p = plugin.manager.get(plugin_id)
    if not p:
        # FIXME: raise proper error
        raise ValueError

    try:
        response = p.client.transaction(transaction_id)
    except grpc.RpcError as e:
        # FIXME: raise proper error
        raise ValueError from e

    status = synse_grpc.utils.to_dict(response)
    status['device'] = device
    return status


async def transactions():
    """Generate the transactions response data.

    Returns:
        list[str]: A list of all currently tracked transaction IDs.
    """
    logger.debug(_('issuing command'), command='TRANSACTIONS')

    return sorted(cache.get_cached_transaction_ids())
