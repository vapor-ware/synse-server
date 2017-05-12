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


class RedfishPowerTestCase(unittest.TestCase):
    """ Test reading and writing the power with the Redfish emulator running
    """
    def test_01_power(self):
        """ Test power control with Redfish.
        """
        # get power reading
        r = http.get(PREFIX + '/power/rack_1/70000000/0100')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertEqual(response['input_power'], 344.0)

        # turn power off:
        r = http.get(PREFIX + '/power/rack_1/70000000/0100/off')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'off')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        #TODO - self.assertEqual(response['input_power'], 0) when emulator changes this value

        # get power reading with status:
        r = http.get(PREFIX + '/power/rack_1/70000000/0100/status')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'off')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        #TODO - self.assertEqual(response['input_power'], 0) when emulator changes this value

        # turn power back on:
        r = http.get(PREFIX + '/power/rack_1/70000000/0100/on')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertEqual(response['input_power'], 344.0)

        # get power reading to check that power is still on:
        r = http.get(PREFIX + '/power/rack_1/70000000/0100')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertEqual(response['input_power'], 344.0)

    def test_02_power(self):
        """ Test power control with Redfish.

        This should fail since the specified action is invalid.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/power/rack_1/70000000/0100/not-action')

    def test_03_power(self):
        """ Test power control with Redfish.
        """
        r = http.get(PREFIX + '/power/rack_1/redfish-emulator/0100')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertEqual(response['input_power'], 344.0)

    def test_04_power(self):
        """ Test power control with Redfish.
        """
        r = http.get(PREFIX + '/power/rack_1/redfish-emulator/power')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertEqual(response['input_power'], 344.0)

    def test_05_power(self):
        """ Test the host info endpoint in Redfish mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/power/rack_1/192.168.3.100/0100')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/power/rack_1/test-3/0100')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/power/rack_1/redfish-emulator/pwoer')