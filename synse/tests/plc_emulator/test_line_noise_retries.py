#!/usr/bin/env python
""" Synse Device Bus Retry (line noise) Tests on Emulator

    Author:  andrew
    Date:    12/5/2015

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

from vapor_common import http
from vapor_common.errors import VaporHTTPError

from synse.tests.test_config import PREFIX


class LineNoiseRetries(unittest.TestCase):
    """ Test retry command (aka '?').
    """

    def test_001_single_read_retry_valid(self):
        """ Single retry, valid retry response
        """
        r = http.get(PREFIX + '/read/thermistor/rack_1/10/01ff')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        # self.assertEqual(response["device_raw"], 656)
        self.assertEqual(response["temperature_c"], 28.78)

    def test_002_single_power_retry_valid(self):
        """ Single retry, valid retry response
        """
        r = http.get(PREFIX + '/power/status/10/02ff')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["pmbus_raw"], "0,0,0,0")

    def test_003_single_version_retry_valid(self):
        """ Single retry, valid retry response
        """
        r = http.get(PREFIX + '/version/rack_1/10')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["firmware_version"], "12345")

    def test_004_double_read_retry_valid(self):
        """ Single retry, valid retry response
        """
        r = http.get(PREFIX + '/read/thermistor/rack_1/11/01ff')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        # self.assertEqual(response["device_raw"], 656)
        self.assertEqual(response["temperature_c"], 28.78)

    def test_005_double_power_retry_valid(self):
        """ Single retry, valid retry response
        """
        r = http.get(PREFIX + '/power/status/11/02ff')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["pmbus_raw"], "0,0,0,0")

    def test_006_double_version_retry_valid(self):
        """ Single retry, valid retry response
        """
        r = http.get(PREFIX + '/version/rack_1/11')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["firmware_version"], "12345")

    def test_007_triple_read_retry_valid(self):
        """ Single retry, valid retry response
        """
        r = http.get(PREFIX + '/read/thermistor/rack_1/12/01ff')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        # self.assertEqual(response["device_raw"], 656)
        self.assertEqual(response["temperature_c"], 28.78)

    def test_008_triple_power_retry_valid(self):
        """ Single retry, valid retry response
        """
        r = http.get(PREFIX + '/power/status/12/02ff')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["pmbus_raw"], "0,0,0,0")

    def test_009_triple_version_retry_valid(self):
        """ Single retry, valid retry response
        """
        r = http.get(PREFIX + '/version/rack_1/12')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["firmware_version"], "12345")

    def test_010_triple_read_retry_fail(self):
        """ Single retry, valid retry response
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/thermistor/rack_1/13/01ff')

        self.assertEqual(ctx.exception.status, 500)

    def test_011_triple_power_retry_fail(self):
        """ Single retry, valid retry response
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/power/status/13/02ff')

        self.assertEqual(ctx.exception.status, 500)

    def test_012_triple_version_retry_fail(self):
        """ Single retry, valid retry response
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/version/rack_1/13')

        self.assertEqual(ctx.exception.status, 500)

    def test_013_triple_read_retry_fail(self):
        """ Single retry, valid retry response
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/thermistor/rack_1/14/01ff')

        self.assertEqual(ctx.exception.status, 500)

    def test_014_triple_power_retry_fail(self):
        """ Single retry, valid retry response
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/power/status/14/02ff')

        self.assertEqual(ctx.exception.status, 500)

    def test_015_triple_version_retry_fail(self):
        """ Single retry, valid retry response
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/version/rack_1/14')

        self.assertEqual(ctx.exception.status, 500)
