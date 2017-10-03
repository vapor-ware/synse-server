#!/usr/bin/env python
""" Test suite for Synse device bus tests

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
import logging
import unittest

from plc_endpoints.test_asset_info import AssetInfoTestCase
from plc_endpoints.test_boot_target import BootTargetTestCase
from plc_endpoints.test_chamber_fan import ChamberFanSpeedTestCase
from plc_endpoints.test_device_read import DeviceReadTestCase
from plc_endpoints.test_fan import FanSpeedTestCase
from plc_endpoints.test_host_info import HostInfoTestCase
from plc_endpoints.test_led import ChassisLedTestCase
from plc_endpoints.test_line_noise import LineNoiseTestCase
from plc_endpoints.test_location import LocationTestCase
from plc_endpoints.test_power import PowerTestCase
from plc_endpoints.test_power_old import OldPowerTestCase
from plc_endpoints.test_scan import ScanTestCase
from plc_endpoints.test_vapor_battery import VaporBatteryTestCase
from plc_endpoints.test_vapor_rectifier import VaporRectifierTestCase
from plc_endpoints.test_version import VersionTestCase

from synse.vapor_common.test_utils import exit_suite, run_suite


def get_suite():
    """ Create an instance of the test suite for device bus tests
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
    suite.addTest(unittest.makeSuite(BootTargetTestCase))
    suite.addTest(unittest.makeSuite(AssetInfoTestCase))
    suite.addTest(unittest.makeSuite(VaporRectifierTestCase))
    suite.addTest(unittest.makeSuite(VaporBatteryTestCase))
    suite.addTest(unittest.makeSuite(ChamberFanSpeedTestCase))
    suite.addTest(unittest.makeSuite(HostInfoTestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-plc-endpoints', get_suite(), loglevel=logging.INFO)
    exit_suite(result)
