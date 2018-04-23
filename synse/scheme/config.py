"""Response scheme for the `config` endpoint."""

from synse import config
from synse.scheme.base_response import SynseResponse


class ConfigResponse(SynseResponse):
    """A ConfigResponse is the response data for a Synse 'config' command.

    The JSON response returned by the Synse endpoint, constructed from
    the data here, should follow the scheme:

    Response Scheme:
        <TODO - WRITE SCHEME FOR RESPONSE>

    Response Example:
        {
        }

    """

    def __init__(self):
        """Constructor for the ConfigResponse class."""
        self.data = {k: v for k, v in config.options.config.items() if not k.startswith('_')}
