"""Response scheme for the `plugins` endpoint."""

from synse.scheme.base_response import SynseResponse


class PluginsResponse(SynseResponse):
    """A PluginsResponse is the response data for the Synse 'plugins' command.

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

    Args:
        data (list): List of dictionaries containing the name, network,
            and address of the registered plugins.
    """

    def __init__(self, data):
        self.data = data
