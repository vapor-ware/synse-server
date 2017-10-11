"""

"""

from synse.scheme.base_response import SynseResponse


class WriteResponse(SynseResponse):
    """

    """

    def __init__(self, transaction):
        """

        Args:
            transaction ():
        """
        self.data = {
            'transaction_id': transaction.id
        }
