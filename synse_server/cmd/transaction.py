
from typing import Any, Dict, List

import synse_grpc.utils
from structlog import get_logger

from synse_server import cache, errors, plugin, utils

logger = get_logger()


async def transaction(transaction_id: str) -> Dict[str, Any]:
    """Generate the transaction response data.

    Args:
        transaction_id: The ID of the transaction to get the status of.

    Returns:
         A dictionary representation of the transaction status response.
    """
    logger.info('issuing command', command='TRANSACTION')

    txn = await cache.get_transaction(transaction_id)
    if not txn:
        raise errors.NotFound(
            f'transaction not found: {transaction_id}',
        )

    plugin_id = txn.get('plugin')
    device = txn.get('device')

    if not plugin_id:
        raise errors.ServerError(
            f'malformed cached transaction ({transaction_id}): "plugin" not defined'
        )

    p = plugin.manager.get(plugin_id)
    if not p:
        raise errors.NotFound(
            f'plugin not found for transaction: {plugin_id}',
        )

    try:
        logger.debug(
            'getting transaction info',
            command='TRANSACTION', device=device, plugin=plugin_id, txn_id=transaction_id,
        )
        with p as client:
            response = client.transaction(transaction_id)
    except Exception as e:
        raise errors.ServerError(
            'error while issuing gRPC request: transaction',
        ) from e

    status = synse_grpc.utils.to_dict(response)
    status['device'] = device
    utils.normalize_write_ctx(status)

    return status


async def transactions() -> List[str]:
    """Generate the transactions response data.

    Returns:
        A list of all currently tracked transaction IDs.
    """
    logger.info('issuing command', command='TRANSACTIONS')

    return sorted(cache.get_cached_transaction_ids())
