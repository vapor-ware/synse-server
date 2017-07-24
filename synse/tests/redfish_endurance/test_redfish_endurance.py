#!/usr/bin/env python
""" Synse API Endurance Tests

    Author:  Morgan Morley Mills
    Date:    02/14/2017

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
import random
import unittest

from synse.tests.test_config import PREFIX
from synse.vapor_common import http


class RedfishEnduranceTestCase(unittest.TestCase):
    """ Testing endurance for Redfish Devices with the emulator running.
    """

    def test_01_endurance(self):
        """ Tests commands that do not require Redfish connection
        """
        request_urls = [
            PREFIX + '/scan',
            PREFIX + '/scan/rack_1',
            PREFIX[:-4] + '/version',
            PREFIX + '/host_info/rack_1/70000000/0100'
        ]
        for x in range(100):
            r = http.get(request_urls[random.randint(0, len(request_urls) - 1)])
            self.assertTrue(http.request_ok(r.status_code))

    def test_02_endurance(self):
        """ Tests commands that require Redfish connection
        """
        request_urls = [
            PREFIX + '/scan/force',
            PREFIX + '/fan/rack_1/70000000/0001',
            PREFIX + '/boot_target/rack_1/70000000/0200',
            PREFIX + '/asset/rack_1/70000000/0200',
            PREFIX + '/read/voltage/rack_1/70000000/0005',
            PREFIX + '/power/rack_1/70000000/0100',
            PREFIX + '/led/rack_1/70000000/0300'
        ]
        for x in range(100):
            r = http.get(request_urls[random.randint(0, len(request_urls) - 1)])
            self.assertTrue(http.request_ok(r.status_code))

    def test_03_endurance(self):
        """ Tests running the same command for different devices many times.
        """
        request_urls = [
            PREFIX + '/read/voltage/rack_1/70000000/0005',
            PREFIX + '/read/fan_speed/rack_1/70000000/0001',
            PREFIX + '/read/temperature/rack_1/70000000/0004',
            PREFIX + '/read/power_supply/rack_1/70000000/0007'
        ]
        for x in range(100):
            r = http.get(request_urls[random.randint(0, len(request_urls) - 1)])
            self.assertTrue(http.request_ok(r.status_code))

    def test_04_endurance(self):
        """ Tests running the same command many times.
        """
        for x in range(100):
            r = http.get(PREFIX + '/led/rack_1/70000000/0300')
            self.assertTrue(http.request_ok(r.status_code))

    def test_05_endurance(self):
        """ Tests turning on and off the chassis LED, which involves PATCHing to the remote device.
        """
        for x in range(50):
            r = http.get(PREFIX + '/led/rack_1/70000000/0300/off')
            self.assertTrue(http.request_ok(r.status_code))

            response = r.json()
            self.assertIsInstance(response, dict)
            self.assertIn('led_state', response)
            self.assertEqual(response['led_state'], 'off')

            r = http.get(PREFIX + '/led/rack_1/70000000/0300/on')
            self.assertTrue(http.request_ok(r.status_code))

            response = r.json()
            self.assertIsInstance(response, dict)
            self.assertIn('led_state', response)
            self.assertEqual(response['led_state'], 'on')

    def test_06_endurance(self):
        """ Tests turning on and off the computer system, which involves POSTing to the remote device.
        """
        for x in range(50):
            r = http.get(PREFIX + '/power/rack_1/70000000/0100/off')
            self.assertTrue(http.request_ok(r.status_code))

            response = r.json()
            self.assertIsInstance(response, dict)
            self.assertIn('power_status', response)
            self.assertEqual(response['power_status'], 'off')

            r = http.get(PREFIX + '/power/rack_1/70000000/0100/on')
            self.assertTrue(http.request_ok(r.status_code))

            response = r.json()
            self.assertIsInstance(response, dict)
            self.assertIn('power_status', response)
            self.assertEqual(response['power_status'], 'on')
