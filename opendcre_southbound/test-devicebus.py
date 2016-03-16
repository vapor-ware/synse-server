#!/usr/bin/env python
"""
Test suite for OpenDCRE Southbound device bus tests

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

from tests.test_device_read import DeviceReadTestCase
from tests.test_version import VersionTestCase
from tests.test_power import PowerTestCase
from tests.test_power_old import OldPowerTestCase
from tests.test_scan import ScanTestCase
from tests.test_line_noise import LineNoiseTestCase
from tests.test_location import LocationTestCase
from tests.test_fan import FanSpeedTestCase
from tests.test_led import ChassisLedTestCase


def get_suite():
    """
    Create an instance of the test suite for device bus tests
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DeviceReadTestCase))
    suite.addTest(unittest.makeSuite(VersionTestCase))
    suite.addTest(unittest.makeSuite(OldPowerTestCase))
    suite.addTest(unittest.makeSuite(ScanTestCase))
    suite.addTest(unittest.makeSuite(LineNoiseTestCase))
    suite.addTest(unittest.makeSuite(PowerTestCase))
    suite.addTest(unittest.makeSuite(LocationTestCase))
    suite.addTest(unittest.makeSuite(FanSpeedTestCase))
    suite.addTest(unittest.makeSuite(ChassisLedTestCase))
    return suite


runner = unittest.TextTestRunner()
runner.run(get_suite())
