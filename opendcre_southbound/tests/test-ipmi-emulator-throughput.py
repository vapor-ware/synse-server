#!/usr/bin/env python
""" Test suite for Vapor Core Southbound IPMI emulator

    Author: Erick Daniszewski
    Date:   10/04/2016

    \\//
     \/apor IO
"""
import unittest
import logging
from vapor_common.test_utils import run_suite, exit_suite

from ipmi_emulator_throughput.test_ipmi_emulator_throughput import IPMIEmulatorThroughputTestCase
from ipmi_emulator_throughput.test_ipmi_emulator_throughput_failures import IPMIEmulatorFailureThroughputTestCase


def get_suite():
    """ Create an instance of the test suite for IPMI emulator
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IPMIEmulatorThroughputTestCase))
    suite.addTest(unittest.makeSuite(IPMIEmulatorFailureThroughputTestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-ipmi-emulator-throughput', get_suite(), loglevel=logging.INFO)
    exit_suite(result)

