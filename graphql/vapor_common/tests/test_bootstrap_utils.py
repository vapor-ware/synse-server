#!/usr/bin/env python
""" Vapor Common Test Runner - Run tests for bootstrap utilities

    Author:  Erick Daniszewski
    Date:    12/11/2016

    \\//
     \/apor IO
"""
import unittest

from bootstrap_utils.test_bootstrap_utils import BootstrapUtilTestCase


def get_suite():
    """ Create an instance of the test suite. """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BootstrapUtilTestCase))
    return suite


runner = unittest.TextTestRunner()
runner.run(get_suite())
