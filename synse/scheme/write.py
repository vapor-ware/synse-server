"""Response scheme for the `write` endpoint."""

from synse.scheme.base_response import SynseResponse


class WriteResponse(SynseResponse):
    """A WriteResponse is the response data for a Synse 'write' command.

    Response Example:
        [
          {
            "context": {
              "action": "state",
              "data": "on"
            },
            "timestamp": "2017-11-08 14:01:53",
            "transaction": "b7jl0b2un4a154rn9u4g"
          }
        ]

    Args:
        transactions (Transactions): The transactions returned from a
            gRPC write request.
    """

    def __init__(self, transactions):
        self.data = []

        for _id, ctx in transactions.items():
            self.data.append({
                'context': {
                    'action': ctx.action,
                    'data': ctx.data
                },
                'transaction': _id
            })
