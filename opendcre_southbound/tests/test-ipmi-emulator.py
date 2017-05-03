#!/usr/bin/env python
""" Test suite for Vapor Core Southbound IPMI emulator tests

    Author: Erick Daniszewski
    Date:   09/07/2016

    \\//
     \/apor IO

-------------------------------
Copyright (C) 2015-17  Vapor IO

This file is part of Synse.

Synse is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

Synse is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Synse.  If not, see <http://www.gnu.org/licenses/>.
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
