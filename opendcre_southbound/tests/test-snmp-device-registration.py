#!/usr/bin/env python
""" Test suite for Vapor Core Southbound SNMP emulator tests

    \\//
     \/apor IO
"""
import logging
import unittest

from snmp_device_registration.test_snmp_device_registration import SnmpDeviceRegistrationTestCase
from vapor_common.test_utils import run_suite, exit_suite


def get_suite():
    """ Create an instance of the test suite for SNMP emulator tests
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SnmpDeviceRegistrationTestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-snmp-device-registration', get_suite(), loglevel=logging.INFO)
    exit_suite(result)
