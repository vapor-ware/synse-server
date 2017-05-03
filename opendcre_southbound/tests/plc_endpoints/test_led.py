#!/usr/bin/env python
""" VaporCORE Southbound API Chassis LED Tests

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

from opendcre_southbound.tests.test_config import PREFIX
from vapor_common import http
from vapor_common.errors import VaporHTTPError


class ChassisLedTestCase(unittest.TestCase):
    """ Test fan speed reads and writes.
    """

    def test_001_read_on(self):
        """ Read a valid on value back from led.
        """
        r = http.get(PREFIX + "/read/led/rack_1/00000030/0001")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["led_state"], 'on')

        r = http.get(PREFIX + "/led/rack_1/00000030/0001")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["led_state"], 'on')

    def test_002_read_off(self):
        """ Read a valid off value back from led.
        """
        r = http.get(PREFIX + "/read/led/rack_1/00000030/0002")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["led_state"], 'off')

        r = http.get(PREFIX + "/led/rack_1/00000030/0002")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["led_state"], 'off')

    def test_003_read_invalid(self):
        """ Read an empty data value, two integers and a string back from the led.
        """
        # empty
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/00000030/0003")

        self.assertEqual(ctx.exception.status, 500)

        # int 2
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/00000030/0003")

        self.assertEqual(ctx.exception.status, 500)

        # int 3
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/00000030/0003")

        self.assertEqual(ctx.exception.status, 500)

        # string "A"
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/00000030/0003")

        self.assertEqual(ctx.exception.status, 500)

        # empty
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/read/led/rack_1/00000030/0003")

        self.assertEqual(ctx.exception.status, 500)

        # int 2
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/read/led/rack_1/00000030/0003")

        self.assertEqual(ctx.exception.status, 500)

        # int 3
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/read/led/rack_1/00000030/0003")

        self.assertEqual(ctx.exception.status, 500)

        # string "A"
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/read/led/rack_1/00000030/0003")

        self.assertEqual(ctx.exception.status, 500)

    def test_004_device_id_representation(self):
        """ Test reading while specifying different representations (same value) for
        the device id
        """
        r = http.get(PREFIX + "/read/led/rack_1/00000030/000000001")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["led_state"], 'on')

        r = http.get(PREFIX + "/led/rack_1/00000030/000000001")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["led_state"], 'on')

    def test_005_read_board_id_invalid(self):
        """ Test read while specifying different invalid representations for
        the board id to ensure out-of-range values are not handled (e.g. set bits
        on packet that should not be set)
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/read/led/rack_1/FFFFFFFF/1FF")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/read/led/rack_1/FFFFFFFFFFFFFFFF/1FF")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/read/led/rack_1/20000000/00001FF")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/read/led/rack_1/10000000/00001FF")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/FFFFFFFF/1FF")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/FFFFFFFFFFFFFFFF/1FF")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/20000000/00001FF")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/10000000/00001FF")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/-10000000/00001FF")

        self.assertEqual(ctx.exception.status, 500)

    def test_006_rack_id_representation(self):
        """ Test read while specifying different values for the rack_id
        """
        r = http.get(PREFIX + "/led/rack_1/00000030/0001")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["led_state"], 'on')

        r = http.get(PREFIX + "/led/STRING_NOT_RELATED_TO_RACK_AT_ALL/00000030/0001")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["led_state"], 'on')

        r = http.get(PREFIX + "/led/STRING WITH SPACES/00000030/0001")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["led_state"], 'on')

        r = http.get(PREFIX + "/led/123456789/00000030/0001")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["led_state"], 'on')

        r = http.get(PREFIX + "/led/123.456/00000030/0001")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["led_state"], 'on')

        r = http.get(PREFIX + "/led/-987654321/00000030/0001")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["led_state"], 'on')

        r = http.get(PREFIX + "/led/acceptable_chars_\@$-_.+!*'(),^&~:;|}{}][]>=<>/00000030/0001")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["led_state"], 'on')

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led//00000030/0001")

        self.assertEqual(ctx.exception.status, 404)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/bad_char?/00000030/0001")

        self.assertEqual(ctx.exception.status, 404)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/bad_char#/00000030/0001")

        self.assertEqual(ctx.exception.status, 404)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/bad_char%/00000030/0001")

        self.assertEqual(ctx.exception.status, 400)

    def test_007_write_ok(self):
        """ Test write with an ok response.
        """
        r = http.get(PREFIX + "/led/rack_1/00000030/0001/on")
        self.assertTrue(http.request_ok(r.status_code))

        r = http.get(PREFIX + "/led/rack_1/00000030/0001/off")
        self.assertTrue(http.request_ok(r.status_code))

    def test_008_write_not_ok(self):
        """ Test write with a failed response.
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/00000030/0002/on")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/00000030/0002/off")

        self.assertEqual(ctx.exception.status, 500)

    def test_009_write_invalid_state(self):
        """ Test write with invalid state values.
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/00000030/0001/blinky")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/00000030/0001/1")

        self.assertEqual(ctx.exception.status, 500)

    def test_010_write_with_bad_response(self):
        """ Test write with bad responses.
        """
        # W2
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/00000030/0003/on")

        self.assertEqual(ctx.exception.status, 500)

        # W3
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/00000030/0003/on")

        self.assertEqual(ctx.exception.status, 500)

        # 1
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/00000030/0003/on")

        self.assertEqual(ctx.exception.status, 500)

        # 0
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/00000030/0003/on")

        self.assertEqual(ctx.exception.status, 500)

        # 2
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/led/rack_1/00000030/0003/on")

        self.assertEqual(ctx.exception.status, 500)
