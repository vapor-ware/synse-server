#!/usr/bin/env python
""" Test suite for Vapor Core Southbound SNMP emulator tests

    \\//
     \/apor IO
"""
import logging
import unittest

from snmp_emulator.test_snmp_emulator import SnmpEmulatorTestCase
from vapor_common.test_utils import run_suite, exit_suite


def get_suite():
    """ Create an instance of the test suite for SNMP emulator tests
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SnmpEmulatorTestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-snmp-emulator', get_suite(), loglevel=logging.INFO)
    exit_suite(result)
