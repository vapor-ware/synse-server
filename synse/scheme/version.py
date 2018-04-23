"""Response scheme for the `version` endpoint."""

from synse.scheme.base_response import SynseResponse
from synse.version import __api_version__, __version__


class VersionResponse(SynseResponse):
    """A VersionResponse is the response data for a Synse 'version' command.

    The JSON response returned by the Synse endpoint, constructed from
    the data here, should follow the scheme:

    Response Scheme:
        {
          "type": "object",
          "properties": {
            "api_version": {
              "$id": "/properties/api_version",
              "type": "string"
            },
            "version": {
              "$id": "/properties/version",
              "type": "string"
            }
          }
        }

    Response Example:
        {
          "version": "2.0.0",
          "api_version": "2.0"
        }

    """

    data = {
        'version': __version__,
        'api_version': __api_version__
    }
