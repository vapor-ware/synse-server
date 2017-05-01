#!/usr/bin/env python
""" Test suite for Vapor Core Southbound tests which do not require a running endpoint to run
"""
import unittest
import logging
from vapor_common.test_utils import run_suite, exit_suite

from utils.test_board_id_utils import BoardIdUtilsTestCase
from utils.test_cache_utils import CacheUtilsTestCase
from utils.test_device_id_utils import DeviceIdUtilsTestCase
from utils.test_device_interface_utils import DeviceInterfaceUtilsTestCase
from utils.test_validation_utils import ValidationUtilsTestCase


def get_suite():
    """ Create an instance of the test suite.
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BoardIdUtilsTestCase))
    suite.addTest(unittest.makeSuite(CacheUtilsTestCase))
    suite.addTest(unittest.makeSuite(DeviceIdUtilsTestCase))
    suite.addTest(unittest.makeSuite(DeviceInterfaceUtilsTestCase))
    suite.addTest(unittest.makeSuite(ValidationUtilsTestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-utils', get_suite(), loglevel=logging.INFO)
    exit_suite(result)
