#!/usr/bin/env python
""" Test suite for Synse bad scan

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

from plc_bad_scan.test_bad_scan import BadScanTestCase
from plc_bad_scan.test_line_noise import LineNoiseTestCase


def get_suite():
    """ Create an instance of the test suite for device bus tests
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(BadScanTestCase))
    suite.addTest(unittest.makeSuite(LineNoiseTestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-plc-bad-scan', get_suite(), loglevel=logging.INFO)
    exit_suite(result)