#!/usr/bin/env python
""" Vapor Common Test Runner - Run tests for Vapor Common's http wrapper

    Author:  Erick Daniszewski
    Date:    12/23/2016

    \\//
     \/apor IO
"""
import unittest

from http.test_http_trusted import HTTPTrustedTestCase
from http.test_http_trusted_no_cert import HTTPTrustedNoCertTestCase
from http.test_http_untrusted import HTTPUntrustedTestCase


def get_suite():
    """ Create an instance of the test suite. """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HTTPUntrustedTestCase))
    suite.addTest(unittest.makeSuite(HTTPTrustedTestCase))
    suite.addTest(unittest.makeSuite(HTTPTrustedNoCertTestCase))
    return suite


runner = unittest.TextTestRunner()
runner.run(get_suite())
