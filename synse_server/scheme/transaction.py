"""Response scheme for the `transaction` endpoint."""

from synse_server.proto import util as putil
from synse_server.scheme.base_response import SynseResponse


class TransactionResponse(SynseResponse):
    """A TransactionResponse is the response data for a Synse
    'transaction' command.

    Response Example:
        {
          "id": "b7jl0b2un4a154rn9u4g",
          "context": {
            "action": "state",
            "raw": ["on"]
          },
          "state": "ok",
          "status": "pending",
          "created": "2017-11-08 14:11:46",
          "updated": "2017-11-08 14:12:04",
          "message": ""
        }

    Args:
        transaction (str): The ID of the transaction.
        context (dict): The write context for the write command the
            transaction is associated with.
        write_response (WriteResponse): The WriteResponse from a gRPC
            transaction check.
    """

    def __init__(self, transaction, context, write_response):
        self.data = {
            'id': transaction,
            'context': context,
            'state': putil.write_state_name(write_response.state),
            'status': putil.write_status_name(write_response.status),
            'created': write_response.created,
            'updated': write_response.updated,
            'message': write_response.message
        }


class TransactionListResponse(SynseResponse):
    """A TransactionListResponse is the response data for Synse Server's
    'list transactions' action.

    Response Example:
        [
            "b7jl0b2un4a154rn9u4g",
            "b7jl0b2un4a154rn9u5a",
            "b7jl0b2un4a154rn9ib2",
        ]

    Args:
        transactions (list[str]): A list of the transaction ids.
    """

    def __init__(self, transactions):
        self.data = transactions
