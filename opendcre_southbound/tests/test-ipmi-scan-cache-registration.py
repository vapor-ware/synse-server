#!/usr/bin/env python
""" Test suite for Vapor Core Southbound IPMI device registration

    Author: Erick Daniszewski
    Date:   01/31/2017

    \\//
     \/apor IO
"""
import unittest
import sys
import logging
from vapor_common.test_utils import run_suite, exit_suite

from ipmi_scan_cache_registration.test_ipmi_scan_cache_registration import IPMIScanCacheRegistrationTestCase


def get_suite():
    """ Create an instance of the test suite for ipmi scan cache registration tests
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IPMIScanCacheRegistrationTestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-ipmi-scan-cache-registration', get_suite(), loglevel=logging.INFO)
    exit_suite(result)
