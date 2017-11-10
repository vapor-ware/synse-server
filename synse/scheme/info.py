"""Response scheme for the /info endpoint.
"""

from synse.scheme.base_response import SynseResponse


class InfoResponse(SynseResponse):
    """An InfoResponse is the response data for a Synse 'info' command.

    The JSON response returned by the Synse endpoint, constructed from
    the data here, should follow the scheme:

    Response Scheme:
        <TODO - WRITE SCHEME FOR RESPONSE>

    Response Example:
        Rack Info
        {
          "rack_id": "rack_1",
          "boards": [
            "00000001",
            "00000002",
            "00000003"
          ]
        }

        Board Info
        {
          "board_id": "00000001",
          "devices": [
            "id1",
            "id2",
            "id3"
          ],
          "location": {
            "rack": "rack_1"
          }
        }

        Device Info
        {
          "device_id": "id1",
          "type": "temperature",
          "model": "MAX11608",
          "manufacturer": "Maxim Integrated",
          "protocol": "i2c",
          "info": "top right thermistor 0",
          "comment": "last serviced 10/21/2017",
          "location": {
            "rack": "rack_1",
            "board": "00000001"
          },
          "output": [
            {
              "type": "temperature",
              "data_type": "float",
              "precision": 2,
              "unit": {
                "name": "degrees celsius",
                "symbol": "C"
              },
              "range": {
                "min": 0,
                "max": 100
              }
            }
          ]
        }

    """

    def __init__(self, data):
        """Constructor for the InfoResponse class.
        """
        self.data = data
