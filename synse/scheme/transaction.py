"""Response scheme for the `transaction` endpoint.
"""

from synse.proto import util as putil
from synse.scheme.base_response import SynseResponse


class TransactionResponse(SynseResponse):
    """A TransactionResponse is the response data for a Synse
    'transaction' command.

    The JSON response returned by the Synse endpoint, constructed from
    the data here, should follow the scheme:

    Response Scheme:
        <TODO - WRITE SCHEME FOR RESPONSE>

    Response Example:
        {
          "id": "b7jl0b2un4a154rn9u4g",
          "context": {
            "action": "blink",
            "raw": ["steady"]
          },
          "state": "ok",
          "status": "pending",
          "created": "2017-11-08 14:11:46",
          "updated": "2017-11-08 14:12:04",
          "message": ""
        }

    """

    def __init__(self, transaction, context, write_response):
        """Constructor for the TransactionResponse class.

        Args:
            transaction ():
            context ():
            write_response ():
        """
        self.data = {
            'id': transaction,
            'context': context,
            'state': putil.write_state_name(write_response.state),
            'status': putil.write_status_name(write_response.status),
            'created': write_response.created,
            'updated': write_response.updated,
            'message': write_response.message
        }