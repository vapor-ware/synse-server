"""Unit tests for the ``synse_server.log`` module."""

import logging

import mock
import structlog

from synse_server import log


def test_setup_logger_defaults():
    logger = structlog.get_logger('synse_server')
    logger.setLevel(logging.DEBUG)

    log.setup_logger()
    assert logger.getEffectiveLevel() == logging.INFO


@mock.patch('synse_server.log.config.options.get', return_value='error')
def test_setup_logger_configured(mock_get):
    log.setup_logger()
    assert structlog.get_logger('synse_server').getEffectiveLevel() == logging.ERROR
    mock_get.assert_called_once_with('logging', 'info')
