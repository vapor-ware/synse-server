#!/usr/bin/env python
"""
Test suite for OpenDCRE Southbound device bus emulator tests

Copyright (C) 2015-16  Vapor IO

This file is part of OpenDCRE.

OpenDCRE is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

OpenDCRE is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenDCRE.  If not, see <http://www.gnu.org/licenses/>.
"""
import unittest

from tests.test_line_noise_retries import LineNoiseRetries
from tests.test_emulator import EmulatorCounterTestCase
from tests.test_emulator_scan import ScanAllTestCase


def get_suite():
    """
    Create an instance of the test suite for device bus emulator tests
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LineNoiseRetries))
    suite.addTest(unittest.makeSuite(EmulatorCounterTestCase))
    suite.addTest(unittest.makeSuite(ScanAllTestCase))
    return suite


runner = unittest.TextTestRunner()
runner.run(get_suite())
