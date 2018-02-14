"""Command handler for the `transaction` route.
"""

import grpc

from synse import cache, errors, plugin
from synse.i18n import gettext
from synse.scheme.transaction import TransactionResponse


async def check_transaction(transaction_id):
    """The handler for the Synse Server "transaction" API command.

    Args:
        transaction_id (str): The id of the transaction to check.

    Returns:
        TransactionResponse: The "transaction" response scheme model.
    """

    transaction = await cache.get_transaction(transaction_id)
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
            gettext('Unable to determine managing plugin for transaction {}.')
            .format(transaction_id)
        )

    _plugin = plugin.get_plugin(plugin_name)
    if not _plugin:
        raise errors.PluginNotFoundError(
            gettext('Unable to find plugin "{}".').format(plugin_name)
        )

    try:
        resp = _plugin.client.check_transaction(transaction_id)
    except grpc.RpcError as ex:
        raise errors.FailedTransactionCommandError(str(ex)) from ex

    return TransactionResponse(transaction_id, context, resp)
