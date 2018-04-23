"""Response scheme for the `test` endpoint."""

from synse import utils
from synse.scheme.base_response import SynseResponse


class TestResponse(SynseResponse):
    """A TestResponse is the response data for a Synse 'test' command.

    The JSON response returned by the Synse endpoint, constructed from
    the data here, should follow the scheme:

    Response Scheme:
        {
          "type": "object",
          "properties": {
            "status": {
              "$id": "/properties/status",
              "type": "string"
            },
            "timestamp": {
              "$id": "/properties/timestamp",
              "type": "string"
            }
          }
        }

    Response Example:
        {
          "status": "ok",
          "timestamp": "2017-09-27 14:33:57.804100"
        }

    """

    data = {
        'status': 'ok'
    }

    def __init__(self):
        """Constructor for the TestResponse class."""
        self.data['timestamp'] = utils.rfc3339now()
