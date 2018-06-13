"""Response scheme for the `capabilities` endpoint."""

from synse.scheme.base_response import SynseResponse


class CapabilitiesResponse(SynseResponse):
    """A CapabilitiesResponse is the response data for the Synse 'capabilities' command.

    Response Example:
        [
          {
            plugin: "",
            devices: [
              {
                kind: "",
                outputs: [
                  ""
                ]
              }
            ]
          }
        ]

    Args:
        data (list): List of dictionaries containing the device kinds and the outputs
            that each kind supports for every registered plugin.
    """

    def __init__(self, data):
        self.data = data
