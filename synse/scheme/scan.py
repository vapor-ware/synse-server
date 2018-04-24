"""Response scheme for the `scan` endpoint."""

from synse.scheme.base_response import SynseResponse


class ScanResponse(SynseResponse):
    """A ScanResponse is the response data for a Synse 'scan' command.

    Response Example:
        {
          "timestamp": "2017-11-10 10:13:45",
          "racks": [
            {
              "rack_id": "rack_1",
              "boards": [
                {
                  "board_id": "5001000d",
                  "devices": [
                    {
                      "device_id": "0001",
                      "device_info": "Rack Differential Pressure Middle",
                      "device_type": "pressure"
                    }
                  ]
                },
                {
                  "board_id": "5001000f",
                  "devices": [
                    {
                      "device_id": "0001",
                      "device_info": "Rack LED",
                      "device_type": "vapor_led"
                    }
                  ]
                },
                {
                  "board_id": "50000001",
                  "devices": [
                    {
                      "device_id": "0001",
                      "device_info": "cec temperature and humidity",
                      "device_type": "humidity"
                    }
                  ]
                }
              ]
            }
          ]
        }

    Args:
        data (dict): The scan data, retrieved from the scan cache.
    """

    def __init__(self, data):
        self.data = data
