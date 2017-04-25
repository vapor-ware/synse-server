#!/usr/bin/env python
""" Vapor Common Test Runner - Run tests for the configuration manager

    Author:  Erick Daniszewski
    Date:    12/06/2016

    \\//
     \/apor IO
"""
import unittest

from config_manager.test_config_manager import ConfigurationManagerTestCase


def get_suite():
    """ Create an instance of the test suite. """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ConfigurationManagerTestCase))
    return suite


runner = unittest.TextTestRunner()
runner.run(get_suite())
