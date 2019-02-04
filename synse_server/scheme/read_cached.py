"""Response scheme for the `readcached` endpoint."""

from synse_server.response import _dumps
from synse_server.scheme.base_response import SynseResponse
from synse_server.scheme.read import ReadResponse


class ReadCachedResponse(SynseResponse):
    """A ReadCachedResponse is the response data for a Synse `readcached` command.

    It effectively augments a `ReadResponse` with the routing info for the
    device that the reading belongs to.

    Response Example:
        {
          "location": {
            "rack": "rack-1",
            "board": "vec",
            "device": "12ea5644d052c6bf1bca3c9864fd8a44"
          },
          "kind": "humidity",
          "info": "",
          "type": "temperature",
          "value": 123,
          "unit": {
            "symbol": "C",
            "name": "degrees celsius"
          },
          "timestamp": "2017-11-10 09:08:07"
        }

    Args:
        device (Device): The device associated with the reading.
        device_reading (Reading): A reading for the cached reading instance.
    """

    def __init__(self, device, device_reading):
        self.device = device
        self.readings = ReadResponse(device, [device_reading.reading])

        read_data = self.readings.data['data']
        if len(read_data) != 1:
            raise ValueError(
                'Expected a single reading for the cache read, but got {}'.format(
                    len(read_data)
                )
            )
        reading = read_data[0]

        self.data = {
            'location': {
                'rack': device_reading.rack,
                'board': device_reading.board,
                'device': device_reading.device,
            },
            'kind': self.readings.data['kind'],
            **reading,
        }

    def dump(self):
        """Dump the response data to a JSON string."""
        return _dumps(self.data)
