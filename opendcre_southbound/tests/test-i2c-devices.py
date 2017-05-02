#!/usr/bin/env python
""" Test suite for Vapor Core Southbound I2C device tests

    Author: Erick Daniszewski
    Date:   02/16/2017

    \\//
     \/apor IO
"""
import logging
import unittest

from vapor_common.test_utils import run_suite, exit_suite

from i2c_devices.test_i2c_sdp610_pressure import SDP610TestCase


def get_suite():
    """ Create an instance of the test suite for I2C device tests
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(SDP610TestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-i2c-devices', get_suite(), loglevel=logging.INFO)
    exit_suite(result)
