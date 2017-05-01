#!/usr/bin/env python
""" Test suite for Vapor Core Southbound tests which do not require a running endpoint to run
"""
import unittest
import logging
from vapor_common.test_utils import run_suite, exit_suite

from location.test_chassis_location import ChassisLocationTestCase


def get_suite():
    """ Create an instance of the test suite for.
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ChassisLocationTestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-location', get_suite(), loglevel=logging.INFO)
    exit_suite(result)
