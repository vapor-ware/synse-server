
import logging

import structlog

from synse_server import log


def test_setup_logger_defaults():
    logger = structlog.get_logger('synse_server')
    logger.setLevel(logging.DEBUG)

    log.setup_logger()
    assert logger.getEffectiveLevel() == logging.INFO


def test_setup_logger_configured(mocker):
    # Mock test data
    mock_get = mocker.patch('synse_server.log.config.options.get', return_value='error')

    # --- Test case -----------------------------
    log.setup_logger()
    assert structlog.get_logger('synse_server').getEffectiveLevel() == logging.ERROR

    mock_get.assert_called_once()
    mock_get.assert_called_with('logging', 'info')
