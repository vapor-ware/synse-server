#!/usr/bin/env python
""" Test suite for Vapor Core Southbound IPMI emulator tests

    Author: Erick Daniszewski
    Date:   09/07/2016

    \\//
     \/apor IO
"""
import unittest
import logging
from vapor_common.test_utils import run_suite, exit_suite

from ipmi_emulator.test_ipmi_emulator import IPMIEmulatorTestCase


def get_suite():
    """ Create an instance of the test suite for IPMI emulator tests
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IPMIEmulatorTestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-ipmi-emulator', get_suite(), loglevel=logging.INFO)
    exit_suite(result)
