"""Response scheme for the `info` endpoint."""

from synse.scheme.base_response import SynseResponse


class InfoResponse(SynseResponse):
    """An InfoResponse is the response data for a Synse 'info' command.

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
          "timestamp": "2018-06-18T13:30:15.6554449Z",
          "uid": "34c226b1afadaae5f172a4e1763fd1a6",
          "kind": "humidity",
          "metadata": {
            "model": "emul8-humidity"
          },
          "plugin": "emulator plugin",
          "info": "Synse Humidity Sensor",
          "location": {
            "rack": "rack-1",
            "board": "vec"
          },
          "output": [
            {
              "name": "humidity",
              "type": "humidity",
              "precision": 3,
              "scaling_factor": 1.0,
              "unit": {
                "name": "percent humidity",
                "symbol": "%"
              }
            },
            {
              "name": "temperature",
              "type": "temperature",
              "precision": 3,
              "scaling_factor": 1.0,
              "unit": {
                "name": "celsius",
                "symbol": "C"
              }
            }
          ]
        }
    """

    def __init__(self, data):
        self.data = data
