#!/usr/bin/env python
""" Test suite for Vapor Core Southbound RS485 emulator tests

    Author: Andrew Cencini
    Date:   10/11/2016

    \\//
     \/apor IO
"""
import unittest
import logging
from vapor_common.test_utils import run_suite, exit_suite

from rs485_emulator.test_rs485_emulator import Rs485EmulatorTestCase


def get_suite():
    """ Create an instance of the test suite for RS485 emulator tests
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Rs485EmulatorTestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-rs485-emulator', get_suite(), loglevel=logging.INFO)
    exit_suite(result)

