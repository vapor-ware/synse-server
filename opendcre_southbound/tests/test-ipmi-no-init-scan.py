#!/usr/bin/env python
""" Test suite for Vapor Core Southbound IPMI with device scan on init disabled.

    Author: Erick Daniszewski
    Date:   10/26/2016

    \\//
     \/apor IO
"""
import unittest
import logging
from vapor_common.test_utils import run_suite, exit_suite

from ipmi_no_init_scan.test_ipmi_no_init_scan import IPMINoInitScanTestCase


def get_suite():
    """ Create an instance of the test suite for no scan during device init
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IPMINoInitScanTestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-ipmi-no-init-scan', get_suite(), loglevel=logging.INFO)
    exit_suite(result)
