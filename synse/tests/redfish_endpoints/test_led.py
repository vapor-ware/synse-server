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


class RedfishLEDTestCase(unittest.TestCase):
    """ Test Chassis LED reads and writes with the Redfish emulator running
    """
    def test_01_led(self):
        """ Test the led endpoint in Redfish mode.
        """
        # Chassis Indicator LED should be off by default
        r = http.get(PREFIX + '/led/rack_1/70000000/0300')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        # This request should turn on the LED.
        r = http.get(PREFIX + '/led/rack_1/70000000/0300/off')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        # Chassis LED should still be on - this tests the emulator.
        r = http.get(PREFIX + '/led/rack_1/70000000/0300')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        # This request should turn off the LED.
        r = http.get(PREFIX + '/led/rack_1/70000000/0300/on')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        # This request should retrieve the information but not change the led_state.
        r = http.get(PREFIX + '/led/rack_1/70000000/0300/no_override')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

    def test_02_led(self):
        """ Test the led endpoint in Redfish mode.
        """
        # fails because not an LED device - power
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/70000000/0100')

    def test_03_led(self):
        """ Test the led endpoint in Redfish mode.
        """
        # fails because not an LED device - system
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/70000000/0200')

    def test_04_led(self):
        """ Test the led endpoint in Redfish mode.
        """
        # fails because not an LED device - fan_speed
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/70000000/0001')

    def test_05_led(self):
        """ Test the led endpoint in Redfish mode.
        """
        # fails because not an LED device - voltage
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/70000000/0005')

    def test_06_led(self):
        """ Test the led endpoint in Redfish mode.
        """
        # fails because not an LED device - temperature
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/70000000/0003')

    def test_07_led(self):
        """ Test the led endpoint in Redfish mode.
        """
        # fails because not an LED device - power_supply
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/70000000/0007')

    def test_08_led(self):
        """ Test the led endpoint in Redfish mode.

        Test passing in an invalid LED command option.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/70000000/0300/non-option')

    def test_09_led(self):
        """ Test the led endpoint in Redfish mode.
        """
        # get LED:
        r = http.get(PREFIX + '/led/rack_1/redfish-emulator/0300')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        # turn on LED:
        r = http.get(PREFIX + '/led/rack_1/redfish-emulator/0300/off')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        # get LED with no_override:
        r = http.get(PREFIX + '/led/rack_1/redfish-emulator/0300/no_override')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        # turn off LED:
        r = http.get(PREFIX + '/led/rack_1/redfish-emulator/0300/on')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        # make sure it's still off:
        r = http.get(PREFIX + '/led/rack_1/redfish-emulator/0300')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

    def test_10_led(self):
        """ Test the led endpoint in Redfish mode.
        """
        # get LED:
        r = http.get(PREFIX + '/led/rack_1/redfish-emulator/led')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        # turn on LED
        r = http.get(PREFIX + '/led/rack_1/redfish-emulator/led/off')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        # get LED using no_override:
        r = http.get(PREFIX + '/led/rack_1/redfish-emulator/led/no_override')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        # turn off LED:
        r = http.get(PREFIX + '/led/rack_1/redfish-emulator/led/on')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        # make sure LED is still off:
        r = http.get(PREFIX + '/led/rack_1/redfish-emulator/led')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

    def test_11_led(self):
        """ Test the host info endpoint in Redfish mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/192.168.3.100/0300/off')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/test-3/0300/off')

    def test_12_led(self):
        """ Test the host info endpoint in Redfish mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/192.168.3.100/led/off')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/test-3/led/off')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/redfish-emulator/ledd/off')