"""Response scheme for the `plugins` endpoint."""

from synse.scheme.base_response import SynseResponse


class PluginsResponse(SynseResponse):
    """A PluginsResponse is the response data for a Synse 'plugins' command.

    The JSON response returned by the Synse endpoint, constructed from
    the data here, should follow the scheme:

    Response Scheme:
        {
          "type": "list",
          "properties": {
            "data": {
              "type": "object",
              "properties": {
                "name": {
                  "$id": "/properties/name",
                  "type": "string"
                },
                "network": {
                  "$id": "/properties/network",
                  "type": "string"
                },
                "address": {
                  "$id": "/properties/address",
                  "type": "string"
                }
              }
            }
          }
        }

    Response Example:
        [
          {
            "name": "i2c",
            "network": "tcp",
            "address": "localhost:5001"
          },
          {
            "name": "rs485",
            "network": "unix",
            "address": "/tmp/synse/proc/rs485.sock"
          }
        ]
    """

    def __init__(self, data):
        """Constructor for the PluginsResponse class.

        Args:
            data (list): List of plugins' objects
        """
        self.data = data
