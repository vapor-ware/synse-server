#!/usr/bin/env python
""" Test suite for Vapor Core Southbound IPMI endpoint tests

    Author: Erick Daniszewski
    Date:   09/27/2016

    \\//
     \/apor IO
"""
import unittest
import logging
from vapor_common.test_utils import run_suite, exit_suite

from ipmi_endpoints.test_ipmi_endpoints import IPMIEndpointsTestCase


def get_suite():
    """ Create an instance of the test suite for ipmi endpoint tests
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IPMIEndpointsTestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-ipmi-endpoints', get_suite(), loglevel=logging.INFO)
    exit_suite(result)

