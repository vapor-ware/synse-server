"""Response scheme for the `test` endpoint."""

from synse import utils
from synse.scheme.base_response import SynseResponse


class TestResponse(SynseResponse):
    """A TestResponse is the response data for a Synse 'test' command.

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
        self.data['timestamp'] = utils.rfc3339now()
