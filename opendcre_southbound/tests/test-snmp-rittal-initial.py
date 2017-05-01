#!/usr/bin/env python
""" Test suite for Vapor Core Southbound SNMP emulator tests

    \\//
     \/apor IO
"""
import logging
import unittest

from snmp_rittal_inital.test_snmp_rittal_initial import SnmpRittalInitialTestCase
from vapor_common.test_utils import run_suite, exit_suite


def get_suite():
    """ Create an instance of the test suite for SNMP emulator tests
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SnmpRittalInitialTestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-snmp-rittal-initial', get_suite(), loglevel=logging.INFO)
    exit_suite(result)
