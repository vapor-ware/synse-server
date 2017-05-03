#!/usr/bin/env python
""" Test suite for Vapor Core Southbound Redfish endpoint tests

    Author: Morgan Morley Mills
    Date:   02/07/2017

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

from redfish_endpoints.test_endpoint import EndpointRunningTestCase
from redfish_endpoints.test_asset import RedfishAssetTestCase
from redfish_endpoints.test_boot_target import RedfishBootTargetTestCase
from redfish_endpoints.test_fan import RedfishFanTestCase
from redfish_endpoints.test_host_info import RedfishHostInfoTestCase
from redfish_endpoints.test_led import RedfishLEDTestCase
from redfish_endpoints.test_power import RedfishPowerTestCase
from redfish_endpoints.test_read import RedfishReadTestCase
from redfish_endpoints.test_scan_all import RedfishScanAllTestCase
from redfish_endpoints.test_scan import RedfishScanTestCase
from redfish_endpoints.test_version import RedfishVersionTestCase

def get_suite():
    """ Create an instance of the test suite for Redfish endpoint tests
    """
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(EndpointRunningTestCase))
    suite.addTest(unittest.makeSuite(RedfishAssetTestCase))
    suite.addTest(unittest.makeSuite(RedfishBootTargetTestCase))
    suite.addTest(unittest.makeSuite(RedfishFanTestCase))
    suite.addTest(unittest.makeSuite(RedfishHostInfoTestCase))
    suite.addTest(unittest.makeSuite(RedfishLEDTestCase))
    suite.addTest(unittest.makeSuite(RedfishPowerTestCase))
    suite.addTest(unittest.makeSuite(RedfishReadTestCase))
    suite.addTest(unittest.makeSuite(RedfishScanAllTestCase))
    suite.addTest(unittest.makeSuite(RedfishScanTestCase))
    suite.addTest(unittest.makeSuite(RedfishVersionTestCase))
    return suite

if __name__ == '__main__':
    result = run_suite('test-redfish-endpoints', get_suite(), loglevel=logging.INFO)
    exit_suite(result)

