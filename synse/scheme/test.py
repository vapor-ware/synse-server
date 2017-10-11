"""

"""

import datetime

from synse.scheme.base_response import SynseResponse


class TestResponse(SynseResponse):
    """The response model for the /synse/<version>/test endpoint.

    Response Scheme:
        {
          "properties": {
            "status": {
              "id": "/properties/status",
              "type": "string"
            },
            "timestamp": {
              "id": "/properties/timestamp",
              "type": "string"
            }
          },
          "type": "object"
        }

    Example Response:
        {
          "status": "ok",
          "timestamp": "2017-09-27 14:33:57.804100"
        }

    """

    data = {
        'status': 'ok'
    }

    def __init__(self):
        """
        """
        self.data['timestamp'] = str(datetime.datetime.utcnow())
