"""

"""

from synse.scheme.base_response import SynseResponse
from synse.version import __api_version__, __version__


class VersionResponse(SynseResponse):
    """The response model for the /version endpoint.

    Response Scheme:
        {
          "properties": {
            "api_version": {
              "id": "/properties/api_version",
              "type": "string"
            },
            "version": {
              "id": "/properties/version",
              "type": "string"
            }
          },
          "type": "object"
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
