#!/usr/bin/env python
""" Vapor Common Test Runner - Run read only tests for checking package installation.

    \\//
     \/apor IO
"""
import unittest
import logging

from package_setup.package_setup import TestVaporCommonPackageSetup
from vapor_common.test_utils import run_suite, exit_suite


def get_suite():
    """ Create an instance of the test suite. """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestVaporCommonPackageSetup))
    return suite


if __name__ == '__main__':
    result = run_suite('test-package-setup', get_suite(), loglevel=logging.ERROR)
    exit_suite(result)
