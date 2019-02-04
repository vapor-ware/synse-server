"""Command handler for the `transaction` route."""

import grpc

from synse_server import cache, errors, plugin
from synse_server.i18n import _
from synse_server.log import logger
from synse_server.scheme import transaction as scheme


async def check_transaction(transaction_id):
    """The handler for the Synse Server "transaction" API command.

    Args:
        transaction_id (str|None): The id of the transaction to check. If
            the ID is None, a list of all transactions currently in the
            cache is returned.

    Returns:
        TransactionResponse: The "transaction" response scheme model.
        TransactionListResponse: The list of all transactions.
    """
    logger.debug(_('Transaction Command (args: {})').format(transaction_id))

    # If we are not given a transaction ID, then we want to return
    # the list of all actively tracked transactions.
    if transaction_id is None:
        all_keys = cache.transaction_cache._cache.keys()
        # Keys in the cache are prepended with 'transaction', so here we get all
        # keys with that prefix and strip the prefix.
        transaction_ids = [k[11:] for k in all_keys if k.startswith('transaction')]
        return scheme.TransactionListResponse(transaction_ids)

    # Otherwise, get the specified transaction.
    transaction = await cache.get_transaction(transaction_id)
    if not transaction:
        raise errors.TransactionNotFoundError(
            _('Transaction with id "{}" not found').format(transaction_id)
        )

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
        raise errors.TransactionNotFoundError(
            _('Unable to determine managing plugin for transaction {}.')
            .format(transaction_id)
        )

    _plugin = plugin.get_plugin(plugin_name)
    if not _plugin:
        raise errors.PluginNotFoundError(
            _('Unable to find plugin "{}"').format(plugin_name)
        )

    try:
        resp = _plugin.client.transaction(transaction_id)
    except grpc.RpcError as ex:
        raise errors.FailedTransactionCommandError(str(ex)) from ex

    return scheme.TransactionResponse(transaction_id, context, resp[0])
