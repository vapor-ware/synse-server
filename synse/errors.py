"""Error definitions for Synse Server."""

from sanic.exceptions import InvalidUsage, NotFound, ServerError

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


class SynseError(Exception):
    """The base exception class for all errors raised by Synse Server."""

    def __init__(self, message, error_id=None):
        super(SynseError, self).__init__(message)
        self.error_id = UNKNOWN if error_id is None else error_id


class SynseServerError(ServerError, SynseError):
    """The base class for all HTTP 500 errors raised by Synse Server.

    All errors that will ultimately issue an HTTP 500 response to the
    caller should either use this class or a subclass of this class.
    Doing so will allow the response to have a JSON payload that
    provides context for the error.

    In general Synse Server 500 errors are returned when there is an
    unrecoverable error when trying to fulfill a request, e.g. unable
    to complete a command.
    """

    def __init__(self, message, error_id=None):
        ServerError.__init__(self, message)
        SynseError.__init__(self, message, error_id)


class SynseNotFoundError(NotFound, SynseError):
    """The base class for all HTTP 404 errors raised by Synse Server.

    All errors that will ultimately issue an HTTP 404 response to the
    caller should either use this class or a subclass of this class.
    Doing so will allow the response to have a JSON payload that
    provides context for the error.

    In general Synse Server 404 errors are returned when either the
    request resource (e.g. a device) or some underlying resource
    (e.g. a plugin) are not found.
    """

    def __init__(self, message, error_id=None):
        NotFound.__init__(self, message)
        SynseError.__init__(self, message, error_id)


class SynseInvalidUsageError(InvalidUsage, SynseError):
    """The base class for all HTTP 400 errors raised by Synse Server.

    All errors that will ultimately issue an HTTP 400 response to the
    caller should either use this class or a subclass of this class.
    Doing so will allow the response to have a JSON payload that
    provides context for the error.

    In general Synse Server 400 errors are returned when information
    given to a route is either invalid (e.g. bad JSON) or does not
    conform to the API spec (e.g. required fields missing, query
    param value format is invalid, etc.)
    """

    def __init__(self, message, error_id=None):
        InvalidUsage.__init__(self, message)
        SynseError.__init__(self, message, error_id)


#
# 400 - Invalid Usage
#

class InvalidArgumentsError(SynseInvalidUsageError):
    """Invalid or unexpected arguments provided."""

    def __init__(self, message):
        super(InvalidArgumentsError, self).__init__(message, INVALID_ARGUMENTS)


class InvalidJsonError(SynseInvalidUsageError):
    """Invalid JSON POSTed to endpoint."""

    def __init__(self, message):
        super(InvalidJsonError, self).__init__(message, INVALID_JSON)


class InvalidDeviceType(SynseInvalidUsageError):
    """A device of some type is not handled by some route."""

    def __init__(self, message):
        super(InvalidDeviceType, self).__init__(message, INVALID_DEVICE_TYPE)


#
# 404 - Not Found
#

class DeviceNotFoundError(SynseNotFoundError):
    """The specified device was not found."""

    def __init__(self, message):
        super(DeviceNotFoundError, self).__init__(message, DEVICE_NOT_FOUND)


class BoardNotFoundError(SynseNotFoundError):
    """The specified board was not found."""

    def __init__(self, message):
        super(BoardNotFoundError, self).__init__(message, BOARD_NOT_FOUND)


class RackNotFoundError(SynseNotFoundError):
    """The specified rack was not found."""

    def __init__(self, message):
        super(RackNotFoundError, self).__init__(message, RACK_NOT_FOUND)


class PluginNotFoundError(SynseNotFoundError):
    """The specified plugin was not found by Synse Server."""

    def __init__(self, message):
        super(PluginNotFoundError, self).__init__(message, PLUGIN_NOT_FOUND)


class TransactionNotFoundError(SynseNotFoundError):
    """The specified transaction was not found."""

    def __init__(self, message):
        super(TransactionNotFoundError, self).__init__(message, TRANSACTION_NOT_FOUND)


#
# 500 - Internal Server Error
#

class FailedInfoCommandError(SynseServerError):
    """Error in executing an "info" command."""

    def __init__(self, message):
        super(FailedInfoCommandError, self).__init__(message, FAILED_INFO_COMMAND)


class FailedReadCommandError(SynseServerError):
    """Error in executing a "read" command."""

    def __init__(self, message):
        super(FailedReadCommandError, self).__init__(message, FAILED_READ_COMMAND)


class FailedWriteCommandError(SynseServerError):
    """Error in executing a "write" command."""

    def __init__(self, message):
        super(FailedWriteCommandError, self).__init__(message, FAILED_WRITE_COMMAND)


class FailedScanCommandError(SynseServerError):
    """Error in executing a "scan" command."""

    def __init__(self, message):
        super(FailedScanCommandError, self).__init__(message, FAILED_SCAN_COMMAND)


class FailedTransactionCommandError(SynseServerError):
    """Error in executing a "transaction" command."""

    def __init__(self, message):
        super(FailedTransactionCommandError, self).__init__(message, FAILED_TRANSACTION_COMMAND)


class InternalApiError(SynseServerError):
    """General error for something that went wrong with the gRPC API."""

    def __init__(self, message):
        super(InternalApiError, self).__init__(message, INTERNAL_API_FAILURE)


class PluginStateError(SynseServerError):
    """Error for Synse Server plugin state being invalid or unexpected."""

    def __init__(self, message):
        super(PluginStateError, self).__init__(message, PLUGIN_STATE_ERROR)


# create a lookup table that maps the code value to a user-friendly string that
# describes the code. the string is the lower-cased version of the variable
# name with underscores replaced with spaces, e.g. SOME_CODE becomes "some code"
codes = {v: k.lower().replace('_', ' ') for k, v in globals().copy().items() if k.isupper()}
