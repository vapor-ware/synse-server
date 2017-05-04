#!/usr/bin/env python
""" Synse Redfish Endpoint Tests

    Author: Morgan Morley Mills, based off IPMI tests by Erick Daniszewski
    Date:   02/06/2017

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

from synse.tests.test_config import PREFIX

from vapor_common import http
from vapor_common.errors import VaporHTTPError


class RedfishFanTestCase(unittest.TestCase):
    """ Test fan reads with the Redfish emulator running
    """
    def test_01_fan(self):
        """ Test the fan endpoint in Redfish mode.
        """
        r = http.get(PREFIX + '/fan/rack_1/70000000/0000')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('speed_rpm', response)
        self.assertEqual(response['speed_rpm'], 2100.0)

        r = http.get(PREFIX + '/fan/rack_1/70000000/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('speed_rpm', response)
        self.assertEqual(response['speed_rpm'], 2050.0)

    def test_02_fan(self):
        """ Test the fan endpoint in Redfish mode.
        """
        # fails because this is not a 'fan' device - power.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/70000000/0100')

    def test_03_fan(self):
        """ Test the fan endpoint in Redfish mode.
        """
        # fails because this is not a 'fan' device - system.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/70000000/0200')

    def test_04_fan(self):
        """ Test the fan endpoint in Redfish mode.
        """
        # fails because this is not a 'fan' device - led.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/70000000/0300')

    def test_05_fan(self):
        """ Test the fan endpoint in Redfish mode.
        """
        # fails because this is not a 'fan' device - voltage.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/70000000/0005')

    def test_06_fan(self):
        """ Test the fan endpoint in Redfish mode.
        """
        # fails because this is not a 'fan' device - power_supply.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/70000000/0007')

    def test_07_fan(self):
        """ Test the fan endpoint in Redfish mode.
        """
        # fails because this is not a 'fan' device - temperature.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/70000000/0003')

    def test_08_fan(self):
        """ Test the fan endpoint in Redfish mode.

        This should fail because the fan device is not present, so it
        cannot be read from.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/70000000/0042')

    def test_09_fan(self):
        """ Test the fan endpoint in Redfish mode.
        """
        # test by device_id:
        r = http.get(PREFIX + '/fan/rack_1/redfish-emulator/0000')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('speed_rpm', response)
        self.assertEqual(response['speed_rpm'], 2100.0)

        r = http.get(PREFIX + '/fan/rack_1/redfish-emulator/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('speed_rpm', response)
        self.assertEqual(response['speed_rpm'], 2050.0)

        # test by device_info:
        r = http.get(PREFIX + '/fan/rack_1/redfish-emulator/BaseBoard System Fan')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('speed_rpm', response)
        self.assertEqual(response['speed_rpm'], 2100.0)

        r = http.get(PREFIX + '/fan/rack_1/redfish-emulator/BaseBoard System Fan Backup')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('speed_rpm', response)
        self.assertEqual(response['speed_rpm'], 2050.0)

    def test_10_fan(self):
        """ Test the host info endpoint in Redfish mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/192.168.3.100/0000')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/redfish-emulator/sys fan')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/redfish-emulator/0042')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/test-1/BaseBoard System Fan')