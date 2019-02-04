"""Test the 'synse_server.errors' Synse Server module."""
# pylint: disable=unsubscriptable-object

from sanic import exceptions

from synse_server import errors


def test_synse_error_unknown():
    """Create a SynseError with no error id specified."""
    e = errors.SynseError('message')

    assert not isinstance(e, exceptions.ServerError)
    assert not isinstance(e, exceptions.InvalidUsage)
    assert not isinstance(e, exceptions.NotFound)
    assert isinstance(e, errors.SynseError)

    assert not hasattr(e, 'status_code')
    assert e.error_id == errors.UNKNOWN
    assert e.args[0] == 'message'


def test_synse_error_device_not_found():
    """Check for DEVICE_NOT_FOUND error"""
    e = errors.DeviceNotFoundError('message')

    assert isinstance(e, exceptions.NotFound)
    assert isinstance(e, errors.SynseError)
    assert isinstance(e, errors.SynseNotFoundError)

    assert e.status_code == 404
    assert e.error_id == errors.DEVICE_NOT_FOUND
    assert e.args[0] == 'message'


def test_synse_error_board_not_found():
    """Check for BOARD_NOT_FOUND error"""
    e = errors.BoardNotFoundError('message')

    assert isinstance(e, exceptions.NotFound)
    assert isinstance(e, errors.SynseError)
    assert isinstance(e, errors.SynseNotFoundError)

    assert e.status_code == 404
    assert e.error_id == errors.BOARD_NOT_FOUND
    assert e.args[0] == 'message'


def test_synse_error_rack_not_found():
    """Check for RACK_NOT_FOUND error"""
    e = errors.RackNotFoundError('message')

    assert isinstance(e, exceptions.NotFound)
    assert isinstance(e, errors.SynseError)
    assert isinstance(e, errors.SynseNotFoundError)

    assert e.status_code == 404
    assert e.error_id == errors.RACK_NOT_FOUND
    assert e.args[0] == 'message'


def test_synse_error_plugin_not_found():
    """Check for PLUGIN_NOT_FOUND error"""
    e = errors.PluginNotFoundError('message')

    assert isinstance(e, exceptions.NotFound)
    assert isinstance(e, errors.SynseError)
    assert isinstance(e, errors.SynseNotFoundError)

    assert e.status_code == 404
    assert e.error_id == errors.PLUGIN_NOT_FOUND
    assert e.args[0] == 'message'


def test_synse_error_transaction_not_found():
    """Check for TRANSACTION_NOT_FOUND error"""
    e = errors.TransactionNotFoundError('message')

    assert isinstance(e, exceptions.NotFound)
    assert isinstance(e, errors.SynseError)
    assert isinstance(e, errors.SynseNotFoundError)

    assert e.status_code == 404
    assert e.error_id == errors.TRANSACTION_NOT_FOUND
    assert e.args[0] == 'message'


def test_synse_error_failed_info_command():
    """Check for FAILED_INFO_COMMAND error"""
    e = errors.FailedInfoCommandError('message')

    assert isinstance(e, exceptions.ServerError)
    assert isinstance(e, errors.SynseError)
    assert isinstance(e, errors.SynseServerError)

    assert e.status_code == 500
    assert e.error_id == errors.FAILED_INFO_COMMAND
    assert e.args[0] == 'message'


def test_synse_error_failed_read_command():
    """Check for FAILED_READ_COMMAND error"""
    e = errors.FailedReadCommandError('message')

    assert isinstance(e, exceptions.ServerError)
    assert isinstance(e, errors.SynseError)
    assert isinstance(e, errors.SynseServerError)

    assert e.status_code == 500
    assert e.error_id == errors.FAILED_READ_COMMAND
    assert e.args[0] == 'message'


def test_synse_error_failed_scan_command():
    """Check for FAILED_SCAN_COMMAND error"""
    e = errors.FailedScanCommandError('message')

    assert isinstance(e, exceptions.ServerError)
    assert isinstance(e, errors.SynseError)
    assert isinstance(e, errors.SynseServerError)

    assert e.status_code == 500
    assert e.error_id == errors.FAILED_SCAN_COMMAND
    assert e.args[0] == 'message'


def test_synse_error_failed_transaction_command():
    """Check for FAILED_TRANSACTION_COMMAND error"""
    e = errors.FailedTransactionCommandError('message')

    assert isinstance(e, exceptions.ServerError)
    assert isinstance(e, errors.SynseError)
    assert isinstance(e, errors.SynseServerError)

    assert e.status_code == 500
    assert e.error_id == errors.FAILED_TRANSACTION_COMMAND
    assert e.args[0] == 'message'


def test_synse_error_failed_write_command():
    """Check for FAILED_WRITE_COMMAND error"""
    e = errors.FailedWriteCommandError('message')

    assert isinstance(e, exceptions.ServerError)
    assert isinstance(e, errors.SynseError)
    assert isinstance(e, errors.SynseServerError)

    assert e.status_code == 500
    assert e.error_id == errors.FAILED_WRITE_COMMAND
    assert e.args[0] == 'message'


def test_synse_error_failed_plugin_command():
    """Check for FAILED_PLUGIN_COMMAND error"""
    e = errors.FailedPluginCommandError('message')

    assert isinstance(e, exceptions.ServerError)
    assert isinstance(e, errors.SynseError)
    assert isinstance(e, errors.SynseServerError)

    assert e.status_code == 500
    assert e.error_id == errors.FAILED_PLUGIN_COMMAND
    assert e.args[0] == 'message'


def test_synse_error_failed_read_cached_command():
    """Check for FAILED_READ_CACHED_COMMAND error"""
    e = errors.FailedReadCachedCommandError('message')

    assert isinstance(e, exceptions.ServerError)
    assert isinstance(e, errors.SynseError)
    assert isinstance(e, errors.SynseServerError)

    assert e.status_code == 500
    assert e.error_id == errors.FAILED_READ_CACHED_COMMAND
    assert e.args[0] == 'message'


def test_synse_error_internal_api():
    """Check for INTERNAL_API_FAILURE error"""
    e = errors.InternalApiError('message')

    assert isinstance(e, exceptions.ServerError)
    assert isinstance(e, errors.SynseError)
    assert isinstance(e, errors.SynseServerError)

    assert e.status_code == 500
    assert e.error_id == errors.INTERNAL_API_FAILURE
    assert e.args[0] == 'message'


def test_synse_error_plugin_state():
    """Check for PLUGIN_STATE_ERROR error"""
    e = errors.PluginStateError('message')

    assert isinstance(e, exceptions.ServerError)
    assert isinstance(e, errors.SynseError)
    assert isinstance(e, errors.SynseServerError)

    assert e.status_code == 500
    assert e.error_id == errors.PLUGIN_STATE_ERROR
    assert e.args[0] == 'message'


def test_synse_error_request_url_not_found():
    """Check for URL_NOT_FOUND error"""
    e = errors.SynseNotFoundError('message', errors.URL_NOT_FOUND)

    assert isinstance(e, exceptions.NotFound)
    assert isinstance(e, errors.SynseError)
    assert isinstance(e, errors.SynseNotFoundError)

    assert e.status_code == 404
    assert e.error_id == errors.URL_NOT_FOUND
    assert e.args[0] == 'message'


def test_synse_error_request_invalid_arguments():
    """Check for INVALID_ARGUMENTS error"""
    e = errors.InvalidArgumentsError('message')

    assert isinstance(e, exceptions.InvalidUsage)
    assert isinstance(e, errors.SynseError)
    assert isinstance(e, errors.SynseInvalidUsageError)

    assert e.status_code == 400
    assert e.error_id == errors.INVALID_ARGUMENTS
    assert e.args[0] == 'message'


def test_synse_error_request_invalid_json():
    """Check for INVALID_JSON error"""
    e = errors.InvalidJsonError('message')

    assert isinstance(e, exceptions.InvalidUsage)
    assert isinstance(e, errors.SynseError)
    assert isinstance(e, errors.SynseInvalidUsageError)

    assert e.status_code == 400
    assert e.error_id == errors.INVALID_JSON
    assert e.args[0] == 'message'


def test_synse_error_request_invalid_device_type():
    """Check for INVALID_DEVICE_TYPE error"""
    e = errors.InvalidDeviceType('message')

    assert isinstance(e, exceptions.InvalidUsage)
    assert isinstance(e, errors.SynseError)
    assert isinstance(e, errors.SynseInvalidUsageError)

    assert e.status_code == 400
    assert e.error_id == errors.INVALID_DEVICE_TYPE
    assert e.args[0] == 'message'
