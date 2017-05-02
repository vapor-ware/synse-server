#!/usr/bin/env python
""" Test suite for Vapor Core Southbound device bus tests
"""
import unittest
import logging
from vapor_common.test_utils import run_suite, exit_suite

from plc_endpoints.test_device_read import DeviceReadTestCase
from plc_endpoints.test_version import VersionTestCase
from plc_endpoints.test_power import PowerTestCase
from plc_endpoints.test_power_old import OldPowerTestCase
from plc_endpoints.test_scan import ScanTestCase
from plc_endpoints.test_line_noise import LineNoiseTestCase
from plc_endpoints.test_location import LocationTestCase
from plc_endpoints.test_fan import FanSpeedTestCase
from plc_endpoints.test_led import ChassisLedTestCase
from plc_endpoints.test_boot_target import BootTargetTestCase
from plc_endpoints.test_asset_info import AssetInfoTestCase
from plc_endpoints.test_vapor_rectifier import VaporRectifierTestCase
from plc_endpoints.test_vapor_battery import VaporBatteryTestCase
from plc_endpoints.test_chamber_led import ChamberLedTestCase
from plc_endpoints.test_chamber_fan import ChamberFanSpeedTestCase
from plc_endpoints.test_host_info import HostInfoTestCase


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
    suite.addTest(unittest.makeSuite(ChamberLedTestCase))
    suite.addTest(unittest.makeSuite(ChamberFanSpeedTestCase))
    suite.addTest(unittest.makeSuite(HostInfoTestCase))
    return suite


if __name__ == '__main__':
    result = run_suite('test-plc-endpoints', get_suite(), loglevel=logging.INFO)
    exit_suite(result)