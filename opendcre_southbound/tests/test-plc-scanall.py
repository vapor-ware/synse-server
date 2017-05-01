#!/usr/bin/env python
""" Test suite for Vapor Core Southbound scan-all protocol tests
"""
import unittest
import logging
from vapor_common.test_utils import run_suite, exit_suite

from plc_scanall.test_scanall import ScanAllTestCase


def get_suite():
    """ Create an instance of the test suite for scan-all protocol tests
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ScanAllTestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-plc-scanall', get_suite(), loglevel=logging.INFO)
    exit_suite(result)

