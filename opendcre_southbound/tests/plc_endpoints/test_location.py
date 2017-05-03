#!/usr/bin/env python
""" VaporCORE Location tests

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


class LocationTestCase(unittest.TestCase):
    """ Test various location scenarios for boards and devices.
    """

    def test_001_valid_board_location(self):
        """ Test simple location(valid board)
        """
        r = http.get(PREFIX + "/location/rack_1/00000000")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["physical_location"]["horizontal"], "unknown")
        self.assertEqual(response["physical_location"]["vertical"], "unknown")
        self.assertEqual(response["physical_location"]["depth"], "unknown")
        self.assertNotIn('chassis_location', response)

    def test_002_valid_board_device_location(self):
        """ Test simple location (valid board, valid device)
        """
        r = http.get(PREFIX + "/location/rack_1/00000000/0000")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["physical_location"]["horizontal"], "unknown")
        self.assertEqual(response["physical_location"]["vertical"], "unknown")
        self.assertEqual(response["physical_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["horiz_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["vert_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["depth"], "unknown")

        r = http.get(PREFIX + "/location/rack_1/00000000/72DF")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["physical_location"]["horizontal"], "unknown")
        self.assertEqual(response["physical_location"]["vertical"], "unknown")
        self.assertEqual(response["physical_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["horiz_pos"], "left")
        self.assertEqual(response["chassis_location"]["vert_pos"], "bottom")
        self.assertEqual(response["chassis_location"]["depth"], "middle")
        self.assertEqual(response["chassis_location"]["server_node"], "unknown")

        r = http.get(PREFIX + "/location/rack_1/00000000/8302")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["physical_location"]["horizontal"], "unknown")
        self.assertEqual(response["physical_location"]["vertical"], "unknown")
        self.assertEqual(response["physical_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["horiz_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["vert_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["server_node"], 3)

        r = http.get(PREFIX + "/location/rack_1/00000000/5555")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["physical_location"]["horizontal"], "unknown")
        self.assertEqual(response["physical_location"]["vertical"], "unknown")
        self.assertEqual(response["physical_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["horiz_pos"], "left")
        self.assertEqual(response["chassis_location"]["vert_pos"], "top")
        self.assertEqual(response["chassis_location"]["depth"], "front")
        self.assertEqual(response["chassis_location"]["server_node"], 'unknown')

        r = http.get(PREFIX + "/location/rack_1/00000000/9F00")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["physical_location"]["horizontal"], "unknown")
        self.assertEqual(response["physical_location"]["vertical"], "unknown")
        self.assertEqual(response["physical_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["horiz_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["vert_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["server_node"], 31)

    def test_003_invalid_board_location(self):
        """ Test simple location (invalid board)
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/location/rack_1/800000000")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/location/rack_1/8000000000")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/location/rack_1/hot_dog")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/location/rack_1/AAAAAAAAA")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/location/rack_1/-1")

        self.assertEqual(ctx.exception.status, 500)

    def test_004_invalid_board_device_location(self):
        """ Test simple location (valid board, invalid device)
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/location/rack_1/00000000/beer")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/location/rack_1/00000000/F00DF00D")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/location/rack_1/00000000/012345")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/location/rack_1/00000000/-01")

        self.assertEqual(ctx.exception.status, 500)

    def test_005_rack_id_representation(self):
        """ Test simple location while specifying different values for the rack_id
        """
        r = http.get(PREFIX + "/location/rack_1/00000000/9F00")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["physical_location"]["horizontal"], "unknown")
        self.assertEqual(response["physical_location"]["vertical"], "unknown")
        self.assertEqual(response["physical_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["horiz_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["vert_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["server_node"], 31)

        r = http.get(PREFIX + "/location/STRING_NOT_RELATED_TO_RACK_AT_ALL/00000000/9F00")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["physical_location"]["horizontal"], "unknown")
        self.assertEqual(response["physical_location"]["vertical"], "unknown")
        self.assertEqual(response["physical_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["horiz_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["vert_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["server_node"], 31)

        r = http.get(PREFIX + "/location/STRING WITH SPACES/00000000/9F00")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["physical_location"]["horizontal"], "unknown")
        self.assertEqual(response["physical_location"]["vertical"], "unknown")
        self.assertEqual(response["physical_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["horiz_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["vert_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["server_node"], 31)

        r = http.get(PREFIX + "/location/123456789/00000000/9F00")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["physical_location"]["horizontal"], "unknown")
        self.assertEqual(response["physical_location"]["vertical"], "unknown")
        self.assertEqual(response["physical_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["horiz_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["vert_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["server_node"], 31)

        r = http.get(PREFIX + "/location/123.456/00000000/9F00")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["physical_location"]["horizontal"], "unknown")
        self.assertEqual(response["physical_location"]["vertical"], "unknown")
        self.assertEqual(response["physical_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["horiz_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["vert_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["server_node"], 31)

        r = http.get(PREFIX + "/location/-987654321/00000000/9F00")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["physical_location"]["horizontal"], "unknown")
        self.assertEqual(response["physical_location"]["vertical"], "unknown")
        self.assertEqual(response["physical_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["horiz_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["vert_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["server_node"], 31)

        r = http.get(PREFIX + "/location/acceptable_chars_\@$-_.+!*'(),^&~:;|}{}][]>=<>/00000000/9F00")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["physical_location"]["horizontal"], "unknown")
        self.assertEqual(response["physical_location"]["vertical"], "unknown")
        self.assertEqual(response["physical_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["horiz_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["vert_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["server_node"], 31)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/location/bad_char?/00000000/9F00")

        self.assertEqual(ctx.exception.status, 404)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/location/bad_char#/00000000/9F00")

        self.assertEqual(ctx.exception.status, 404)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/location/bad_char%/00000000/9F00")

        self.assertEqual(ctx.exception.status, 400)
