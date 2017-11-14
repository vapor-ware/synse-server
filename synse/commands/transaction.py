"""Command handler for the `transaction` route.
"""

import grpc

from synse import errors
from synse.cache import get_transaction
from synse.plugin import get_plugin
from synse.scheme.transaction import TransactionResponse


async def check_transaction(transaction_id):
    """The handler for the Synse Server "transaction" API command.

    Args:
        transaction_id (str): The id of the transaction to check.

    Returns:
        TransactionResponse: The "transaction" response scheme model.
    """

    transaction = await get_transaction(transaction_id)
    plugin_name = transaction.get('plugin')
    context = transaction.get('context')

    if not plugin_name:
        # TODO - in the future, what we could do is attempt sending the transaction
        #   request to *all* of the known plugins. this could be useful in the event
        #   that synse goes down. since everything is just stored in memory, a new
        #   synse instance will have lost the transaction cache.
        #
        #   alternatively, we could think about having an internal api command to
        #   essentially dump the active transactions so that we can rebuild the cache.
        raise errors.SynseError('Unable to determine process for the given transaction.', errors.TRANSACTION_NOT_FOUND)

    plugin = get_plugin(plugin_name)
    if not plugin:
        raise errors.SynseError(
            'Unable to find plugin named "{}" to read.'.format(
                plugin_name), errors.PLUGIN_NOT_FOUND
        )

    try:
        resp = plugin.client.check_transaction(transaction_id)
    except grpc.RpcError as ex:
        raise errors.SynseError('Failed to issue a transaction check request.', errors.FAILED_TRANSACTION_COMMAND) from ex

    return TransactionResponse(transaction_id, context, resp)
