"""Response scheme for the /info endpoint.
"""

from synse.scheme.base_response import SynseResponse


class InfoResponse(SynseResponse):
    """An InfoResponse is the response data for a Synse 'info' command.

    The JSON response returned by the Synse endpoint, constructed from
    the data here, should follow the scheme:

    Response Scheme:
        <TODO - WRITE SCHEME FOR RESPONSE>

    Response Example:
        {
        }

    """

    def __init__(self, data):
        """Constructor for the InfoResponse class.
        """
        self.data = data
