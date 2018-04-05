"""Response scheme for the `write` endpoint.
"""

from synse.scheme.base_response import SynseResponse


class WriteResponse(SynseResponse):
    """A WriteResponse is the response data for a Synse 'write' command.

    The JSON response returned by the Synse endpoint, constructed from
    the data here, should follow the scheme:

    Response Scheme:
        <TODO - WRITE SCHEME FOR RESPONSE>

    Response Example:
        [
          {
            "context": {
              "action": "state",
              "raw": ["on"]
            },
            "timestamp": "2017-11-08 14:01:53",
            "transaction": "b7jl0b2un4a154rn9u4g"
          }
        ]

    """

    def __init__(self, transactions):
        """Constructor for the WriteResponse class.

        Args:
            transactions ():
        """
        self.data = []

        for _id, ctx in transactions.items():
            self.data.append({
                'context': {
                    'action': ctx.action,
                    'raw': ctx.raw
                },
                'transaction': _id
            })
