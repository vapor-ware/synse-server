#!/usr/bin/env python
""" Test suite for Vapor Core Southbound IPMI device registration

    Author: Erick Daniszewski
    Date:   10/26/2016

    \\//
     \/apor IO
"""
import unittest
import logging
from vapor_common.test_utils import run_suite, exit_suite

from ipmi_device_registration.test_ipmi_device_registration import IPMIDeviceRegistrationTestCase


def get_suite():
    """ Create an instance of the test suite for ipmi device registration tests
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IPMIDeviceRegistrationTestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-ipmi-device-registration', get_suite(), loglevel=logging.INFO)
    exit_suite(result)
