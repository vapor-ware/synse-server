"""Response scheme for the `scan` endpoint."""

from synse.scheme.base_response import SynseResponse


class ScanResponse(SynseResponse):
    """A ScanResponse is the response data for a Synse 'scan' command.

    Response Example:
        "racks": [
            {
              "id": "rack-1",
              "boards": [
                {
                  "id": "vec",
                  "devices": [
                    {
                      "id": "eb100067acb0c054cf877759db376b03",
                      "info": "Synse Temperature Sensor 1",
                      "type": "temperature"
                    },
                    {
                      "id": "83cc1efe7e596e4ab6769e0c6e3edf88",
                      "info": "Synse Temperature Sensor 2",
                      "type": "temperature"
                    },
                    {
                      "id": "329a91c6781ce92370a3c38ba9bf35b2",
                      "info": "Synse Temperature Sensor 4",
                      "type": "temperature"
                    },
                    {
                      "id": "f97f284037b04badb6bb7aacd9654a4e",
                      "info": "Synse Temperature Sensor 5",
                      "type": "temperature"
                    },
                    {
                      "id": "eb9a56f95b5bd6d9b51996ccd0f2329c",
                      "info": "Synse Fan",
                      "type": "fan"
                    },
                    {
                      "id": "f52d29fecf05a195af13f14c7306cfed",
                      "info": "Synse LED",
                      "type": "led"
                    },
                    {
                      "id": "d29e0bd113a484dc48fd55bd3abad6bb",
                      "info": "Synse Backup LED",
                      "type": "led"
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
