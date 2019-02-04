"""Response scheme for the `version` endpoint."""

from synse_server.scheme.base_response import SynseResponse
from synse_server.version import __api_version__, __version__


class VersionResponse(SynseResponse):
    """A VersionResponse is the response data for a Synse 'version' command.

    Response Example:
        {
          "version": "2.0.0",
          "api_version": "v2"
        }
    """

    data = {
        'version': __version__,
        'api_version': __api_version__
    }
