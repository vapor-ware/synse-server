#!/usr/bin/env python
""" Synse Boot Target Tests

    Author:  andrew
    Date:    3/17/2016

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


class BootTargetTestCase(unittest.TestCase):
    """ Test boot target sets and gets.
    """
    def test_001_read_ok(self):
        """ Read a valid boot target back.
        """
        r = http.get(PREFIX + '/boot_target/rack_1/00000040/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['target'], 'no_override')

        r = http.get(PREFIX + '/boot_target/rack_1/00000040/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/rack_1/00000040/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['target'], 'pxe')

    def test_002_set_ok(self):
        """ Set boot target to valid value (will always return 'hdd' due to emulator config.
        """
        r = http.get(PREFIX + '/boot_target/rack_1/00000040/0002/hdd')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/rack_1/00000040/0002/pxe')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/rack_1/00000040/0002/no_override')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['target'], 'hdd')

    def test_003_read_empty(self):
        """ Read an empty data value back.
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/rack_1/00000040/0003')

        self.assertEqual(ctx.exception.status, 500)

    def test_004_invalid_value(self):
        """ What happens when a weird values returned? (negative)
        """
        # 'B3'
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/rack_1/00000040/0003')

        self.assertEqual(ctx.exception.status, 500)

        # '2'
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/rack_1/00000040/0003')

        self.assertEqual(ctx.exception.status, 500)

        # '3'
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/rack_1/00000040/0003')

        self.assertEqual(ctx.exception.status, 500)

        # 'B?'
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/rack_1/00000040/0003')

        self.assertEqual(ctx.exception.status, 500)

    def test_005_set_not_ok(self):
        """ What happens when a bad value is set? (negative)
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/rack_1/00000040/0002/hard_disk')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/rack_1/00000040/0002/pixie')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/rack_1/00000040/0002/B0')

        self.assertEqual(ctx.exception.status, 500)

    def test_006_device_id_representation(self):
        """ Test reading while specifying different representations (same value) for
        the device id
        """
        r = http.get(PREFIX + '/boot_target/rack_1/00000040/000000002')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/rack_1/00000040/000000002')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['target'], 'hdd')

    def test_007_read_board_id_invalid(self):
        """ Test read while specifying different invalid representations for the board id
        to ensure out-of-range values are not handled (e.g. set bits on packet that should
        not be set)
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/rack_1/FFFFFFFF/1FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/rack_1/FFFFFFFFFFFFFFFF/1FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/rack_1/20000000/00001FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/rack_1/10000000/00001FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/rack_1/FFFFFFFF/1FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/rack_1/FFFFFFFFFFFFFFFF/1FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/rack_1/20000000/00001FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/rack_1/10000000/00001FF')

        self.assertEqual(ctx.exception.status, 500)

    def test_008_write_bad_board(self):
        """ Test write with bad board.
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/rack_1/00000039/0001/hdd')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/rack_1/-00000029/0001/hdd')

        self.assertEqual(ctx.exception.status, 500)

    def test_009_rack_id_representation(self):
        """ Test read while specifying different values for the rack_id
        """
        r = http.get(PREFIX + '/boot_target/rack_1/00000040/0002')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/STRING_NOT_RELATED_TO_RACK_AT_ALL/00000040/0002')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/STRING WITH SPACES/00000040/0002')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/123456789/00000040/0002')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/123.456/00000040/0002')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/-987654321/00000040/0002')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/acceptable_chars_\@$-_.+!*\'(),^&~:;|}{}][]>=<>/00000040/0002')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['target'], 'hdd')

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target//00000040/0002')

        self.assertEqual(ctx.exception.status, 404)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/bad_char?/00000040/0002')

        self.assertEqual(ctx.exception.status, 404)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/bad_char#/00000040/0002')

        self.assertEqual(ctx.exception.status, 404)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/bad_char%/00000040/0002')

        self.assertEqual(ctx.exception.status, 404)

    def test_010_write_bad_device(self):
        """ Test write with bad device.
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/rack_1/00000040/00FF/pxe')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/rack_1/00000040/-00FF/no_override')

        self.assertEqual(ctx.exception.status, 500)

    def test_011_write_with_bad_response(self):
        """ Test write with bad response.
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/boot_target/rack_1/00000040/0003/hdd')

        self.assertEqual(ctx.exception.status, 500)
