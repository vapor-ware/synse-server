"""Response scheme for the /scan endpoint.
"""

from synse.scheme.base_response import SynseResponse


class ScanResponse(SynseResponse):
    """A ScanResponse is the response data for a Synse 'scan' command.

    The JSON response returned by the Synse endpoint, constructed from
    the data here, should follow the scheme:

    Response Scheme:
        <TODO - WRITE SCHEME FOR RESPONSE>

    Response Example:
        {
        }

    """

    def __init__(self, data):
        """Constructor for the ScanResponse class.

        Args:
            data ():
        """
        self.data = data
