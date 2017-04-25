#!/usr/bin/env python
""" Vapor Common Test Runner - Run tests for trust utilities

    Author:  Erick Daniszewski
    Date:    12/06/2016

    \\//
     \/apor IO
"""
import unittest

from trust_utils.test_trust_utils import TrustUtilsTestCase


def get_suite():
    """ Create an instance of the test suite. """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TrustUtilsTestCase))
    return suite


runner = unittest.TextTestRunner()
runner.run(get_suite())
