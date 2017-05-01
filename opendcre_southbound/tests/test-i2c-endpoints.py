#!/usr/bin/env python
""" Test suite for Vapor Core Southbound I2C endpoint tests

    Author: Andrew Cencini
    Date:   10/19/2016

    \\//
     \/apor IO
"""
import unittest
import logging
from vapor_common.test_utils import run_suite, exit_suite

from i2c_endpoints.test_i2c_endpoints import I2CEndpointsTestCase


def get_suite():
    """ Create an instance of the test suite for I2C endpoint tests
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(I2CEndpointsTestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-i2c-endpoints', get_suite(), loglevel=logging.INFO)
    exit_suite(result)
