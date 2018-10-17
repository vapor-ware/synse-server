"""Response scheme for the `readcached` endpoint."""

from synse.response import _dumps
from synse.scheme.base_response import SynseResponse
from synse.scheme.read import ReadResponse


class ReadCachedResponse(SynseResponse):
    """A ReadCachedResponse is the response data for a Synse `readcached` command.

    It effectively augments a `ReadResponse` with the routing info for the
    device that the reading belongs to.

    Response Example:
        {
          "provenance": {
            "rack": "rack-1",
            "board": "vec",
            "device": "12ea5644d052c6bf1bca3c9864fd8a44"
          },
          "kind": "humidity",
          "data": [
            {
              "info": "",
              "type": "temperature",
              "value": 123,
              "unit": {
                "symbol": "C",
                "name": "degrees celsius"
              },
              "timestamp": "2017-11-10 09:08:07"
            },
            {
              "info": "",
              "type": "humidity",
              "value": 123,
              "unit": {
                "symbol": "%",
                "name": "percent"
              },
              "timestamp": "2017-11-10 09:08:07"
            }
          ]
        }

    Args:
        device (Device): The device associated with the reading.
        device_reading (Reading): A reading for the cached reading instance.
    """

    def __init__(self, device, device_reading):
        self.device = device
        self.reading = ReadResponse(device, [device_reading.reading])

        self.data = {
            'provenance': {
                'rack': device_reading.rack,
                'board': device_reading.board,
                'device': device_reading.device,
            },
            **self.reading.data
        }

    def dump(self):
        """Dump the response data to a JSON string."""
        return _dumps(self.data)
