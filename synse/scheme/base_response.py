"""Base response model for all Synse Server response schemes.
"""

from synse.response import json


class SynseResponse(object):
    """SynseResponse is the base object for all implemented response
    schemes.

    It defines a `data` member which holds the response data that will
    be returned. Additionally, it provides a `to_json` method which
    converts the data to a JSON response.
    """

    data = {}

    def to_json(self):
        """Convert the response scheme data to JSON.

        Returns:
            sanic.HTTPResponse: The Sanic endpoint response with the given
                body encoded as JSON.
        """
        return json(self.data)
