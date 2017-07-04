#!/usr/bin/env python
""" Synse API Chamber LED Tests

    Author:  andrew
    Date:    3/24/2016

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


class ChamberLedTestCase(unittest.TestCase):
    """ Test chamber LED.
    """
    def test_001_read_valid(self):
        """ Read a valid on value back from chamber led.
        """
        r = http.get(PREFIX + "/led/rack_1/00000070/0001/on/ffffff/steady")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["led_state"], 'on')
        self.assertEqual(response["led_color"], 'ffffff')
        self.assertEqual(response["blink_state"], 'steady')

        r = http.get(PREFIX + "/led/rack_1/00000070/0001/off/000000/no_override")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["led_state"], 'off')
        self.assertEqual(response["led_color"], '000000')
        self.assertEqual(response["blink_state"], 'steady')

        r = http.get(PREFIX + "/led/rack_1/00000070/0001/no_override/7ac055/blink")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["led_state"], 'off')
        self.assertEqual(response["led_color"], '7ac055')
        self.assertEqual(response["blink_state"], 'blink')

        r = http.get(PREFIX + "/led/rack_1/00000070/0001/on/0beef0/no_override")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["led_state"], 'on')
        self.assertEqual(response["led_color"], '0beef0')
        self.assertEqual(response["blink_state"], 'blink')

    def test_002_read_valid(self):
        """ Read a valid on value back from chamber led. This is the same test as
        above, just with the color value set to no-override, to ensure that reading
        with a no-override color set works.
        """
        r = http.get(PREFIX + "/led/rack_1/00000070/0001/on/no_override/steady")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["led_state"], 'on')
        self.assertEqual(response["led_color"], 'ffffff')
        self.assertEqual(response["blink_state"], 'steady')

        r = http.get(PREFIX + "/led/rack_1/00000070/0001/off/no_override/no_override")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["led_state"], 'off')
        self.assertEqual(response["led_color"], '000000')
        self.assertEqual(response["blink_state"], 'steady')

        r = http.get(PREFIX + "/led/rack_1/00000070/0001/no_override/no_override/blink")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["led_state"], 'off')
        self.assertEqual(response["led_color"], '7ac055')
        self.assertEqual(response["blink_state"], 'blink')

        r = http.get(PREFIX + "/led/rack_1/00000070/0001/on/no_override/no_override")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["led_state"], 'on')
        self.assertEqual(response["led_color"], '0beef0')
        self.assertEqual(response["blink_state"], 'blink')

    def test_003_format_invalid(self):
        """ Send invalid command format (chassis LED) (negative).
        """
        # bad command
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/00000070/0001/on")

        self.assertEqual(ctx.exception.status, 500)

        # bad color value
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/00000070/0001/on/ffffffff/no_override")

        self.assertEqual(ctx.exception.status, 500)

        # bad led_state
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/00000070/0001/tacos/no_override/no_override")

        self.assertEqual(ctx.exception.status, 500)

        # bad blink_state
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/00000070/0001/on/no_override/fading")

        self.assertEqual(ctx.exception.status, 500)

    def test_004_read_invalid(self):
        """ Read an empty data value (negative).
        """
        # empty
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/00000070/0002/on/no_override/no_override")

        self.assertEqual(ctx.exception.status, 500)

    def test_005_device_id_representation(self):
        """ Test reading while specifying different representations (same value) for
        the device id
        """
        r = http.get(PREFIX + "/led/rack_1/00000070/000000001/on/0beef0/no_override")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["led_state"], 'on')

        r = http.get(PREFIX + "/led/rack_1/00000070/000000001/off/000000/blink")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["led_state"], 'off')

    def test_006_read_board_id_invalid(self):
        """ Test read while specifying different invalid representations for the board id
        to ensure out-of-range values are not handled (e.g. set bits on packet that should
        not be set)
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/FFFFFFFF/1FF/no_override/no_override/no_override")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/FFFFFFFFFFFFFFFF/1FF/no_override/no_override/no_override")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/20000000/00001FF/no_override/no_override/no_override")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/10000000/00001FF/no_override/no_override/no_override")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/FFFFFFFF/1FF/no_override/no_override/no_override")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/FFFFFFFFFFFFFFFF/1FF/no_override/no_override/no_override")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/20000000/00001FF/no_override/no_override/no_override")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/10000000/00001FF/no_override/no_override/no_override")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/-10000000/00001FF/no_override/no_override/no_override")

        self.assertEqual(ctx.exception.status, 500)

    def test_007_write_with_bad_response(self):
        """ Test write with bad response.
        """
        # junk,data,for,you
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/00000070/0003/on/no_override/no_override")

        self.assertEqual(ctx.exception.status, 500)
