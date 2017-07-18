#!/usr/bin/env python
""" Synse API Power Tests - Using DEPRECATED power command syntax.

    Author:  andrew
    Date:    1/23/2016

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

from synse.vapor_common import http
from synse.vapor_common.errors import VaporHTTPError

from synse.tests.test_config import PREFIX


class OldPowerTestCase(unittest.TestCase):
    """ Power control/status tests.
    """

    def test_001_get_power_status(self):
        # expected raw 0
        r = http.get(PREFIX + '/power/status/0000001E/01FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['pmbus_raw'], '0,0,0,0')
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertEqual(response['under_voltage'], False)

        # expected raw 64 (0x40) - when off, power_ok and under_voltage
        # and under_current don't have any meaning
        r = http.get(PREFIX + '/power/status/0000001E/01FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['pmbus_raw'], '64,0,0,0')
        self.assertEqual(response['power_status'], 'off')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertEqual(response['under_voltage'], False)

        # expected raw 2048 (0x800) - power problem but not
        # something related to under voltage or over current condition
        r = http.get(PREFIX + '/power/status/0000001E/01FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['pmbus_raw'], '2048,0,0,0')
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], False)
        self.assertEqual(response['over_current'], False)
        self.assertEqual(response['under_voltage'], False)

        # expected raw 2048+8=2056 (0x1010) - power problem due to under voltage
        r = http.get(PREFIX + '/power/status/0000001E/01FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['pmbus_raw'], '2056,0,0,0')
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], False)
        self.assertEqual(response['over_current'], False)
        self.assertEqual(response['under_voltage'], True)

        # expected raw 2048+16=2064 (0x1020) - power problem due to over current
        r = http.get(PREFIX + '/power/status/0000001E/01FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['pmbus_raw'], '2064,0,0,0')
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], False)
        self.assertEqual(response['over_current'], True)
        self.assertEqual(response['under_voltage'], False)

        # expected raw 2072 (0x1030)
        r = http.get(PREFIX + '/power/status/0000001E/01FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['pmbus_raw'], '2072,0,0,0')
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], False)
        self.assertEqual(response['over_current'], True)
        self.assertEqual(response['under_voltage'], True)

    def test_002_power_on(self):
        r = http.get(PREFIX + '/power/on/0000001E/01FF')
        self.assertTrue(http.request_ok(r.status_code))

    def test_003_power_cycle(self):
        r = http.get(PREFIX + '/power/cycle/0000001E/01FF')
        self.assertTrue(http.request_ok(r.status_code))

    def test_004_power_off(self):
        r = http.get(PREFIX + '/power/off/0000001E/01FF')
        self.assertTrue(http.request_ok(r.status_code))

    def test_005_valid_device_invalid_type(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/power/status/0000001E/02FF')

        self.assertEqual(ctx.exception.status, 500)

    def test_006_invalid_device(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/power/status/0000001E/03FF')

        self.assertEqual(ctx.exception.status, 500)

    @unittest.skip('After implementing rack_id to the synse endpoints, the invalid command \
    sent in this request is evaluated as a rack_id and a status is returned. Thus no error')
    def test_007_invalid_command(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/power/invalid/0000001E/01FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/power/cyle/0000001E/01FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/power/xxx/0000001E/01FF')

        self.assertEqual(ctx.exception.status, 500)

    def test_008_no_power_data(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/power/status/0000001E/03FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/power/status/0000001E/04FF')

        self.assertEqual(ctx.exception.status, 500)

    def test_009_weird_data(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/power/status/0000001E/05FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/power/status/0000001E/06FF')

        self.assertEqual(ctx.exception.status, 500)

    def test_010_power_board_id_representation(self):
        """ Test power status while specifying different representations (same value) for
        the board id
        """
        r = http.get(PREFIX + '/power/status/1E/01FF')
        self.assertTrue(http.request_ok(r.status_code))

        r = http.get(PREFIX + '/power/status/001E/01FF')
        self.assertTrue(http.request_ok(r.status_code))

        r = http.get(PREFIX + '/power/status/00001E/01FF')
        self.assertTrue(http.request_ok(r.status_code))

        r = http.get(PREFIX + '/power/status/0000000001E/01FF')
        self.assertTrue(http.request_ok(r.status_code))

    def test_011_power_device_id_representation(self):
        """ Test power status while specifying different representations (same value) for
        the board id
        """
        r = http.get(PREFIX + '/power/status/0000001E/1FF')
        self.assertTrue(http.request_ok(r.status_code))

        r = http.get(PREFIX + '/power/status/0000001E/01FF')
        self.assertTrue(http.request_ok(r.status_code))

        r = http.get(PREFIX + '/power/status/0000001E/00001FF')
        self.assertTrue(http.request_ok(r.status_code))

    def test_012_power_board_id_invalid(self):
        """ Test power status while specifying different invalid representations for
        the board id to ensure out-of-range values are not handled (e.g. set bits on
        packet that should not be set)
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/power/status/FFFFFFFF/1FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/power/status/FFFFFFFFFFFFFFFF/1FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/power/status/20000000/00001FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/power/status/10000000/00001FF')

        self.assertEqual(ctx.exception.status, 500)
