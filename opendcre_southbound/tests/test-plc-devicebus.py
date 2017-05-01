#!/usr/bin/env python
""" Test suite for Vapor Core Southbound tests which do not require a running endpoint to run
"""
import unittest
import logging
from vapor_common.test_utils import run_suite, exit_suite

from plc_devicebus.test_devicebus import DevicebusTestCase


def get_suite():
    """ Create an instance of the test suite.
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DevicebusTestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-plc-devicebus', get_suite(), loglevel=logging.INFO)
    exit_suite(result)
