#!/usr/bin/env python
""" Synse Asset Info Tests

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


class AssetInfoTestCase(unittest.TestCase):
    """ Test asset information retrieval.
    """

    def test_001_read_ok(self):
        """ Read valid asset info back.
        """
        r = http.get(PREFIX + '/asset/rack_1/00000050/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertEqual(response['board_info']['manufacturer'], 'Vapor IO')
        self.assertEqual(response['product_info']['version'], 'v1.2.0')

    def test_002_read_empty(self):
        """ Read an empty data value back.
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/asset/rack_1/00000050/0002')

        self.assertEqual(ctx.exception.status, 500)

    def test_003_invalid_value(self):
        """ What happens when a weird values returned? (negative)
        """
        # 'just a string'
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/asset/rack_1/00000050/0003')

        self.assertEqual(ctx.exception.status, 500)

        # '1234'
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/asset/rack_1/00000050/0003')

        self.assertEqual(ctx.exception.status, 500)

        # '3'
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/asset/rack_1/00000050/0003')

        self.assertEqual(ctx.exception.status, 500)

        # 'B?'
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/asset/rack_1/00000050/0003')

        self.assertEqual(ctx.exception.status, 500)

    def test_004_device_id_representation(self):
        """ Test reading while specifying different representations (same value) for
        the device id
        """
        r = http.get(PREFIX + '/asset/rack_1/00000050/000000001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertEqual(response['board_info']['manufacturer'], 'Vapor IO')
        self.assertEqual(response['product_info']['version'], 'v1.2.0')

        r = http.get(PREFIX + '/asset/rack_1/00000050/1')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertEqual(response['board_info']['manufacturer'], 'Vapor IO')
        self.assertEqual(response['product_info']['version'], 'v1.2.0')

    def test_005_read_board_id_invalid(self):
        """ Test read while specifying different invalid representations for
        the board id to ensure out-of-range values are not handled (e.g. set
        bits on packet that should not be set)
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/asset/rack_1/FFFFFFFF/1FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/asset/rack_1/FFFFFFFFFFFFFFFF/1FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/asset/rack_1/20000000/00001FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/asset/rack_1/10000000/00001FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/asset/rack_1/FFFFFFFF/1FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/asset/rack_1/FFFFFFFFFFFFFFFF/1FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/asset/rack_1/20000000/00001FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/asset/rack_1/10000000/00001FF')

        self.assertEqual(ctx.exception.status, 500)

    def test_006_bad_board(self):
        """ Test with bad board.
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/asset/rack_1/00000059/0001')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/asset/rack_1/-00000059/0001')

        self.assertEqual(ctx.exception.status, 500)

    def test_007_bad_device(self):
        """ Test with bad device.
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/asset/rack_1/00000050/00FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/asset/rack_1/00000050/-00FF')

        self.assertEqual(ctx.exception.status, 500)

    def test_008_rack_id_representation(self):
        """ Test while specifying different values for the rack_id
        """
        r = http.get(PREFIX + '/asset/rack_1/00000050/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['board_info']['manufacturer'], 'Vapor IO')
        self.assertEqual(response['product_info']['version'], 'v1.2.0')

        r = http.get(PREFIX + '/asset/STRING_NOT_RELATED_TO_RACK_AT_ALL/00000050/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['board_info']['manufacturer'], 'Vapor IO')
        self.assertEqual(response['product_info']['version'], 'v1.2.0')

        r = http.get(PREFIX + '/asset/STRING WITH SPACES/00000050/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['board_info']['manufacturer'], 'Vapor IO')
        self.assertEqual(response['product_info']['version'], 'v1.2.0')

        r = http.get(PREFIX + '/asset/123456789/00000050/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['board_info']['manufacturer'], 'Vapor IO')
        self.assertEqual(response['product_info']['version'], 'v1.2.0')

        r = http.get(PREFIX + '/asset/123.456/00000050/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['board_info']['manufacturer'], 'Vapor IO')
        self.assertEqual(response['product_info']['version'], 'v1.2.0')

        r = http.get(PREFIX + '/asset/-987654321/00000050/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['board_info']['manufacturer'], 'Vapor IO')
        self.assertEqual(response['product_info']['version'], 'v1.2.0')

        r = http.get(PREFIX + '/asset/acceptable_chars_\@$-_.+!*\'(),^&~:;|}{}][]>=<>/00000050/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['board_info']['manufacturer'], 'Vapor IO')
        self.assertEqual(response['product_info']['version'], 'v1.2.0')

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/asset//00000050/0001')

        self.assertEqual(ctx.exception.status, 404)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/asset/bad_char?/00000050/0001')

        self.assertEqual(ctx.exception.status, 404)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/asset/bad_char#/00000050/0001')

        self.assertEqual(ctx.exception.status, 404)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/asset/bad_char%/00000050/0001')

        self.assertEqual(ctx.exception.status, 404)
