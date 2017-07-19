#!/usr/bin/env python
""" Synse API Fan Speed Tests

    Author:  andrew
    Date:    2/23/2016

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
from synse.vapor_common import http
from synse.vapor_common.errors import VaporHTTPError


class FanSpeedTestCase(unittest.TestCase):
    """ Test fan speed reads and writes.
    """

    def test_001_read_ok(self):
        """ Read a valid value back from fan.
        """
        r = http.get(PREFIX + '/read/fan_speed/rack_1/00000028/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['speed_rpm'], 4100)

        r = http.get(PREFIX + '/fan/rack_1/00000028/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['speed_rpm'], 4100)

    def test_002_read_string(self):
        """ Read a string value back from fan (negative).
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/fan_speed/rack_1/00000028/0002')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/fan/rack_1/00000028/0002')

        self.assertEqual(ctx.exception.status, 500)

    def test_003_read_empty(self):
        """ Read an empty data value back from the fan.
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/fan_speed/rack_1/00000028/0003')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/fan/rack_1/00000028/0003')

        self.assertEqual(ctx.exception.status, 500)

    def test_004_long_value(self):
        """ What happens when a large integer is returned? (positive)
        """
        r = http.get(PREFIX + '/read/fan_speed/rack_1/00000028/0004')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['speed_rpm'], 12345678901234567890)

        r = http.get(PREFIX + '/fan/rack_1/00000028/0004')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['speed_rpm'], 12345678901234567890)

    def test_005_negative_number(self):
        """ What happens when a negative number is returned? (positive)
        """
        r = http.get(PREFIX + '/read/fan_speed/rack_1/00000028/0005')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['speed_rpm'], -12345)

        r = http.get(PREFIX + '/fan/rack_1/00000028/0005')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['speed_rpm'], -12345)

    def test_006_device_id_representation(self):
        """ Test reading while specifying different representations (same value) for
        the device id
        """
        r = http.get(PREFIX + '/read/fan_speed/rack_1/00000028/000000001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['speed_rpm'], 4100)

        r = http.get(PREFIX + '/fan/rack_1/00000028/000000001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['speed_rpm'], 4100)

    def test_007_read_board_id_invalid(self):
        """ Test read while specifying different invalid representations for
        the board id to ensure out-of-range values are not handled (e.g. set bits
        on packet that should not be set)
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/fan_speed/rack_1/FFFFFFFF/1FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/fan_speed/rack_1/FFFFFFFFFFFFFFFF/1FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/fan_speed/rack_1/20000000/00001FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/fan_speed/rack_1/10000000/00001FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/fan/rack_1/FFFFFFFF/1FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/fan/rack_1/FFFFFFFFFFFFFFFF/1FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/fan/rack_1/20000000/00001FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/fan/rack_1/10000000/00001FF')

        self.assertEqual(ctx.exception.status, 500)

    def test_008_rack_id_representation(self):
        """ Test read while specifying different values for the rack_id
        """
        r = http.get(PREFIX + '/fan/rack_1/00000028/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['speed_rpm'], 4100)

        r = http.get(PREFIX + '/fan/STRING_NOT_RELATED_TO_RACK_AT_ALL/00000028/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['speed_rpm'], 4100)

        r = http.get(PREFIX + '/fan/STRING WITH SPACES/00000028/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['speed_rpm'], 4100)

        r = http.get(PREFIX + '/fan/123456789/00000028/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['speed_rpm'], 4100)

        r = http.get(PREFIX + '/fan/123.456/00000028/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['speed_rpm'], 4100)

        r = http.get(PREFIX + '/fan/-987654321/00000028/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['speed_rpm'], 4100)

        r = http.get(PREFIX + '/fan/acceptable_chars_\@$-_.+!*\'(),^&~:;|}{}][]>=<>/00000028/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['speed_rpm'], 4100)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/fan//00000028/0001')

        self.assertEqual(ctx.exception.status, 404)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/fan/bad_char?/00000028/0001')

        self.assertEqual(ctx.exception.status, 404)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/fan/bad_char#/00000028/0001')

        self.assertEqual(ctx.exception.status, 404)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/fan/bad_char%/00000028/0001')

        self.assertEqual(ctx.exception.status, 404)

    def test_009_write_ok(self):
        """ Test write with an ok response.
        """
        r = http.get(PREFIX + '/fan/rack_1/00000028/0001/4100')
        self.assertTrue(http.request_ok(r.status_code))

    def test_010_write_long(self):
        """ Test write with long numbers.
        """
        r = http.get(PREFIX + '/fan/rack_1/00000028/0001/00000000004100')
        self.assertTrue(http.request_ok(r.status_code))

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/fan/rack_1/00000028/0001/12345678901234567890')

        self.assertEqual(ctx.exception.status, 500)

    def test_011_write_neg_num(self):
        """ Test write with negative numbers.
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/fan/rack_1/00000028/0001/-4100')

        self.assertEqual(ctx.exception.status, 500)

    def test_012_write_string(self):
        """ Test write with string.
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/fan/rack_1/00000028/0001/faster')

        self.assertEqual(ctx.exception.status, 500)

    def test_013_write_bad_board(self):
        """ Test write with bad board.
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/fan/rack_1/00000029/0001/4100')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/fan/rack_1/-00000029/0001/4100')

        self.assertEqual(ctx.exception.status, 500)

    def test_014_write_bad_device(self):
        """ Test write with bad device.
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/fan/rack_1/00000028/00FF/4100')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/fan/rack_1/00000028/-00FF/4100')

        self.assertEqual(ctx.exception.status, 500)

    def test_015_write_with_bad_response(self):
        """ Test write with bad response.
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/fan/rack_1/00000028/0002/4100')

        self.assertEqual(ctx.exception.status, 500)
