#!/usr/bin/env python
""" Test suite for OpenDCRE device bus emulator tests
"""
import unittest
import logging
from vapor_common.test_utils import run_suite, exit_suite

from plc_emulator.test_line_noise_retries import LineNoiseRetries
from plc_emulator.test_emulator import EmulatorCounterTestCase
from plc_emulator.test_emulator_scan import ScanAllTestCase


def get_suite():
    """ Create an instance of the test suite for device bus emulator tests
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LineNoiseRetries))
    suite.addTest(unittest.makeSuite(EmulatorCounterTestCase))
    suite.addTest(unittest.makeSuite(ScanAllTestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-plc-emulator', get_suite(), loglevel=logging.INFO)
    exit_suite(result)

