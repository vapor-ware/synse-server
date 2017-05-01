#!/usr/bin/env python
""" Test suite for Vapor Core Southbound Redfish endpoint tests

    Author: Morgan Morley Mills
    Date:   02/14/2017

    \\//
     \/apor IO
"""
import unittest
import logging

from vapor_common.test_utils import run_suite, exit_suite
from redfish_endurance.test_redfish_endurance import RedfishEnduranceTestCase


def get_suite():
    """ Create an instance of the test suite for Redfish endpoint tests
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(RedfishEnduranceTestCase))
    return suite

if __name__ == '__main__':
    result = run_suite('test-redfish-endurance', get_suite(), loglevel=logging.INFO)
    exit_suite(result)
