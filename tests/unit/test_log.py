
import logging
from unittest import mock

from synse_server import log


def test_setup_logger_defaults():
    log.logger.setLevel(logging.DEBUG)

    log.setup_logger()
    assert log.logger.getEffectiveLevel() == logging.INFO


@mock.patch('synse_server.log.config.options.get', return_value='error')
def test_setup_logger_configured(patched_get):
    log.setup_logger()
    assert log.logger.getEffectiveLevel() == logging.ERROR

    patched_get.assert_called_once()
    patched_get.assert_called_with('logging', 'info')
