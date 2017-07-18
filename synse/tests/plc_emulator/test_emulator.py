#!/usr/bin/env python
""" Synse API Device Bus Emulator Tests

    Author:  Erick Daniszewski
    Date:    8/25/2015

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


class EmulatorCounterTestCase(unittest.TestCase):
    """ Tests to ensure the emulator counter behaves as is expected and does
    not get changed erroneously.
    """

    def test_001_read_same_board_same_device(self):
        """ Test reading a single thermistor device repeatedly to make sure it
        increments sequentially.
        """
        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/01FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 100)

        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/01FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 101)

        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/01FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 102)

    def test_002_read_same_board_diff_device(self):
        """ Test reading thermistor devices on the same board but different devices,
        where both devices have the same length of responses and repeatable=true.
        One device being tested does not start at the first response since
        previous tests have incremented its counter.
        """
        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/01FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 103)

        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/03FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 200)

        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/01FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 104)

        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/03FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 201)

    def test_003_read_diff_board_diff_device(self):
        """ Test reading thermistor devices on different boards, where both
        devices have the same length of responses and repeatable=true. One
        device being tested does not start at the first response since
        previous tests have incremented its counter.
        """
        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/03FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 202)

        r = http.get(PREFIX + '/read/temperature/rack_1/00000003/02FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 800)

        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/03FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 203)

        r = http.get(PREFIX + '/read/temperature/rack_1/00000003/02FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 801)

    def test_004_read_until_wraparound(self):
        """ Test incrementing the counter on alternating devices (humidity
        and thermistor), both where repeatable=true, but where the length
        of the responses list differ.
        """
        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/0CFF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 600)

        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/0AFF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 500)

        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/0CFF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 601)

        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/0AFF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 501)

        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/0CFF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 602)

        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/0AFF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 502)

        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/0CFF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 603)

        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/0AFF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 503)

        # counter should wrap back around here, since len(responses) has
        # been exceeded.
        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/0CFF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 600)

        # counter should not wrap around for this device, since len(responses)
        # has not been exceeded
        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/0AFF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 504)

        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/0CFF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 601)

        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/0AFF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 505)

    def test_005_power_same_board_diff_device(self):
        """ Test incrementing the counter on alternating power devices,
        one where repeatable=true, and one where repeatable=false
        """
        r = http.get(PREFIX + '/power/status/00000001/06FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['pmbus_raw'], '0,0,0,0')

        r = http.get(PREFIX + '/power/status/00000001/07FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['pmbus_raw'], '0,0,0,0')

        r = http.get(PREFIX + '/power/status/00000001/06FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['pmbus_raw'], '64,0,0,0')

        r = http.get(PREFIX + '/power/status/00000001/07FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['pmbus_raw'], '64,0,0,0')

        r = http.get(PREFIX + '/power/status/00000001/06FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['pmbus_raw'], '2048,0,0,0')

        r = http.get(PREFIX + '/power/status/00000001/07FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['pmbus_raw'], '2048,0,0,0')

        # repeatable=true, so the counter should cycle back around
        r = http.get(PREFIX + '/power/status/00000001/06FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['pmbus_raw'], '0,0,0,0')

        # repeatable=false, so should not the counter back around
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/power/status/00000001/07FF')

        self.assertEqual(ctx.exception.status, 500)

    def test_006_power_read_alternation(self):
        """ Test incrementing the counter alternating between a power cmd and
        a read cmd, both where repeatable=true.
        """
        # perform three http on the thermistor to get the count different from
        # the start count of the power
        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/08FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 300)

        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/08FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 301)

        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/08FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 302)

        # start alternating between power and thermistor
        r = http.get(PREFIX + '/power/status/00000001/05FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['pmbus_raw'], '0,0,0,0')

        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/08FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 303)

        r = http.get(PREFIX + '/power/status/00000001/05FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['pmbus_raw'], '64,0,0,0')

        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/08FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 304)

        r = http.get(PREFIX + '/power/status/00000001/05FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['pmbus_raw'], '2048,0,0,0')

        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/08FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 305)

        r = http.get(PREFIX + '/power/status/00000001/05FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['pmbus_raw'], '2056,0,0,0')

        r = http.get(PREFIX + '/read/temperature/rack_1/00000001/08FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 306)
