#!/usr/bin/env python
""" Vapor Common Test Runner - Run tests for cache utilities

    Author:  Erick Daniszewski
    Date:    12/22/2016

    \\//
     \/apor IO
"""
import unittest

from cache_utils.test_cache_utils import CacheUtilsTestCase


def get_suite():
    """ Create an instance of the test suite. """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(CacheUtilsTestCase))
    return suite


runner = unittest.TextTestRunner()
runner.run(get_suite())
