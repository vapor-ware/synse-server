"""
"""

from synse.response import json


class SynseResponse(object):
    """
    """

    data = {}

    def to_json(self):
        """
        """
        return json(self.data)
