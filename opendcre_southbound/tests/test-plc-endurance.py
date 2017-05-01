#!/usr/bin/env python
""" Test suite for Vapor Core Southbound endurance tests
"""
import unittest
import logging
from vapor_common.test_utils import run_suite, exit_suite

from plc_endurance.test_endurance import EnduranceTestCase
from plc_endurance.test_threaded import ThreadedTestCase
from plc_endurance.test_throughput import ThroughputTestCase


def get_suite():
    """ Create an instance of the test suite for endurance tests
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EnduranceTestCase))
    suite.addTest(unittest.makeSuite(ThreadedTestCase))
    suite.addTest(unittest.makeSuite(ThroughputTestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-plc-endurance', get_suite(), loglevel=logging.INFO)
    exit_suite(result)

