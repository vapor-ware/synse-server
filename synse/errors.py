"""

"""

from sanic.exceptions import ServerError


class SynseError(ServerError):
    """
    """

    def __init__(self, message, error_id=None):
        super(SynseError, self).__init__(message)
        self.error_id = UNKNOWN if error_id is None else error_id


DEVICE_NOT_FOUND = 4000
BOARD_NOT_FOUND = 4001
RACK_NOT_FOUND = 4002
PROCESS_NOT_FOUND = 4003
TRANSACTION_NOT_FOUND = 4003


FAILED_HEALTH_COMMAND = 5000
FAILED_INFO_COMMAND = 5001
FAILED_LOCATION_COMMAND = 5002
FAILED_READ_COMMAND = 5003
FAILED_SCAN_COMMAND = 5004
FAILED_TRANSACTION_COMMAND = 5005
FAILED_WRITE_COMMAND = 5006

INTERNAL_API_FAILURE = 6000

UNKNOWN = 0

INVALID_ARGUMENTS = 3

URL_NOT_FOUND = 7000


# create a lookup table that maps the code value to a user-friendly string that
# describes the code. the string is the lower-cased version of the variable
# name with underscores replaced with spaces, e.g. SOME_CODE becomes "some code"
codes = {v: k.lower().replace('_', ' ') for k, v in globals().copy().items() if k.isupper()}
