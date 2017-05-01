#!/usr/bin/env python
""" Test suite for OpenDCRE bad scan
"""
import unittest
import logging
from vapor_common.test_utils import run_suite, exit_suite

from plc_bad_scan.test_bad_scan import BadScanTestCase
from plc_bad_scan.test_line_noise import LineNoiseTestCase


def get_suite():
    """ Create an instance of the test suite for device bus tests
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BadScanTestCase))
    suite.addTest(unittest.makeSuite(LineNoiseTestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-plc-bad-scan', get_suite(), loglevel=logging.INFO)
    exit_suite(result)