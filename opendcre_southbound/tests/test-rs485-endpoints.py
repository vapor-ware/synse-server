#!/usr/bin/env python
""" Test suite for Vapor Core Southbound RS485 endpoint tests

    Author: Andrew Cencini
    Date:   10/12/2016

    \\//
     \/apor IO
"""
import unittest
import logging
from vapor_common.test_utils import run_suite, exit_suite

from rs485_endpoints.test_rs485_endpoints import Rs485EndpointsTestCase


def get_suite():
    """ Create an instance of the test suite for RS485 emulator tests
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Rs485EndpointsTestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-rs485-endpoints', get_suite(), loglevel=logging.INFO)
    exit_suite(result)
