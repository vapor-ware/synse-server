"""

"""

from synse.proto import util as putil
from synse.scheme.base_response import SynseResponse


class TransactionResponse(SynseResponse):
    """

    """

    def __init__(self, write_status):
        """

        Args:
            write_status ():
        """
        self.data = {
            'timestamp': write_status.timestamp,
            'status': putil.write_status_name(write_status.status),
            'state': putil.write_state_name(write_status.state)
        }
