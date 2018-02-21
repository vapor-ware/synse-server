"""Error definitions for Synse Server.
"""

from sanic.exceptions import ServerError

# Not Found type errors
DEVICE_NOT_FOUND = 4000
BOARD_NOT_FOUND = 4001
RACK_NOT_FOUND = 4002
PLUGIN_NOT_FOUND = 4003
TRANSACTION_NOT_FOUND = 4004

# Failed Command type errors
FAILED_INFO_COMMAND = 5000
FAILED_READ_COMMAND = 5001
FAILED_SCAN_COMMAND = 5002
FAILED_TRANSACTION_COMMAND = 5003
FAILED_WRITE_COMMAND = 5004

# Internal API (gRPC) errors
INTERNAL_API_FAILURE = 6000

# Plugin related errors
PLUGIN_STATE_ERROR = 6500

# Request related errors
URL_NOT_FOUND = 3000
INVALID_ARGUMENTS = 3001
INVALID_JSON = 3002
INVALID_DEVICE_TYPE = 3003

# Unknown type error - this is used as the fallback
UNKNOWN = 0


class SynseError(ServerError):
    """General error raised within Synse Server.

    Everything that raises an exception within Synse Server should ultimately
    propagate this (or a subclass of this) up to the route handler. There, it
    will propagate up through Sanic handling and will result in a 500 error
    response with JSON.
    """

    def __init__(self, message, error_id=None):
        super(SynseError, self).__init__(message)
        self.error_id = UNKNOWN if error_id is None else error_id


class InvalidArgumentsError(SynseError):
    """Invalid or unexpected arguments provided."""

    def __init__(self, message):
        super(InvalidArgumentsError, self).__init__(message, INVALID_ARGUMENTS)


class InvalidJsonError(SynseError):
    """Invalid JSON POSTed to endpoint."""

    def __init__(self, message):
        super(InvalidJsonError, self).__init__(message, INVALID_JSON)


class InvalidDeviceType(SynseError):
    """A device of some type is not handled by some route."""

    def __init__(self, message):
        super(InvalidDeviceType, self).__init__(message, INVALID_DEVICE_TYPE)


class DeviceNotFoundError(SynseError):
    """The specified device was not found."""

    def __init__(self, message):
        super(DeviceNotFoundError, self).__init__(message, DEVICE_NOT_FOUND)


class BoardNotFoundError(SynseError):
    """The specified board was not found."""

    def __init__(self, message):
        super(BoardNotFoundError, self).__init__(message, BOARD_NOT_FOUND)


class RackNotFoundError(SynseError):
    """The specified rack was not found."""

    def __init__(self, message):
        super(RackNotFoundError, self).__init__(message, RACK_NOT_FOUND)


class PluginNotFoundError(SynseError):
    """The specified plugin was not found by Synse Server."""

    def __init__(self, message):
        super(PluginNotFoundError, self).__init__(message, PLUGIN_NOT_FOUND)


class TransactionNotFoundError(SynseError):
    """The specified transaction was not found."""

    def __init__(self, message):
        super(TransactionNotFoundError, self).__init__(message, TRANSACTION_NOT_FOUND)


class FailedInfoCommandError(SynseError):
    """Error in executing an "info" command."""

    def __init__(self, message):
        super(FailedInfoCommandError, self).__init__(message, FAILED_INFO_COMMAND)


class FailedReadCommandError(SynseError):
    """Error in executing a "read" command."""

    def __init__(self, message):
        super(FailedReadCommandError, self).__init__(message, FAILED_READ_COMMAND)


class FailedWriteCommandError(SynseError):
    """Error in executing a "write" command."""

    def __init__(self, message):
        super(FailedWriteCommandError, self).__init__(message, FAILED_WRITE_COMMAND)


class FailedScanCommandError(SynseError):
    """Error in executing a "scan" command."""

    def __init__(self, message):
        super(FailedScanCommandError, self).__init__(message, FAILED_SCAN_COMMAND)


class FailedTransactionCommandError(SynseError):
    """Error in executing a "transaction" command."""

    def __init__(self, message):
        super(FailedTransactionCommandError, self).__init__(message, FAILED_TRANSACTION_COMMAND)


class InternalApiError(SynseError):
    """General error for something that went wrong with the gRPC API."""

    def __init__(self, message):
        super(InternalApiError, self).__init__(message, INTERNAL_API_FAILURE)


class PluginStateError(SynseError):
    """Error for Synse Server plugin state being invalid or unexpected."""

    def __init__(self, message):
        super(PluginStateError, self).__init__(message, PLUGIN_STATE_ERROR)


# create a lookup table that maps the code value to a user-friendly string that
# describes the code. the string is the lower-cased version of the variable
# name with underscores replaced with spaces, e.g. SOME_CODE becomes "some code"
codes = {v: k.lower().replace('_', ' ') for k, v in globals().copy().items() if k.isupper()}
