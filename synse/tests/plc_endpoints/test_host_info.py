#!/usr/bin/env python
""" Synse API Host Info Tests

    Author:  andrew
    Date:    3/28/2016

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


class HostInfoTestCase(unittest.TestCase):
    """ Test host info.
    """

    def test_001_read_valid(self):
        """ Read a valid host info back.
        """
        r = http.get(PREFIX + '/host_info/rack_1/00000090/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['hostnames'][0], 'hostname1')
        self.assertEqual(response['ip_addresses'][0], '192.168.1.1')

        r = http.get(PREFIX + '/host_info/rack_1/00000090/0002')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['hostnames'][0], 'test-server0')
        self.assertEqual(response['ip_addresses'][0], '10.10.1.15')

        r = http.get(PREFIX + '/host_info/rack_1/00000090/0003')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['hostnames'][0], 'test-server00')
        self.assertEqual(response['hostnames'][1], 'test-server01')
        self.assertEqual(response['ip_addresses'][0], '10.10.1.15')
        self.assertEqual(response['ip_addresses'][1], '1.1.1.1')

    def test_002_read_invalid(self):
        """ Read an empty data value, and invalid data back.
        """
        # invalid-string
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/host_info/rack_1/00000090/0004')

        self.assertEqual(ctx.exception.status, 500)

        # empty
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/host_info/rack_1/00000090/0005')

        self.assertEqual(ctx.exception.status, 500)

    def test_003_device_id_representation(self):
        """ Test reading while specifying different representations (same value) for
        the device id
        """
        r = http.get(PREFIX + '/host_info/rack_1/00000090/000000000000001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['hostnames'][0], 'hostname1')
        self.assertEqual(response['ip_addresses'][0], '192.168.1.1')

        r = http.get(PREFIX + '/host_info/rack_1/000000000000090/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['hostnames'][0], 'hostname1')
        self.assertEqual(response['ip_addresses'][0], '192.168.1.1')

    def test_004_read_board_id_invalid(self):
        """ Test read while specifying different invalid representations for
        the board id to ensure out-of-range values are not handhost_info (e.g. set
        bits on packet that should not be set)
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/host_info/rack_1/FFFFFFFF/1FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/host_info/rack_1//FFFFFFFFFFFFFFFF/1FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/host_info/rack_1/20000000/00001FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/host_info/rack_1/10000000/00001FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/host_info/rack_1/FFFFFFFF/1FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/host_info/rack_1/FFFFFFFFFFFFFFFF/1FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/host_info/rack_1/20000000/00001FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/host_info/rack_1/10000000/00001FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/host_info/rack_1/-10000000/00001FF')

        self.assertEqual(ctx.exception.status, 500)

    def test_005_rack_id_representation(self):
        """ Test read while specifying different values for the rack_id
        """
        r = http.get(PREFIX + '/host_info/rack_1/00000090/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['hostnames'][0], 'hostname1')
        self.assertEqual(response['ip_addresses'][0], '192.168.1.1')

        r = http.get(PREFIX + '/host_info/STRING_NOT_RELATED_TO_RACK_AT_ALL/00000090/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['hostnames'][0], 'hostname1')
        self.assertEqual(response['ip_addresses'][0], '192.168.1.1')

        r = http.get(PREFIX + '/host_info/STRING WITH SPACES/00000090/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['hostnames'][0], 'hostname1')
        self.assertEqual(response['ip_addresses'][0], '192.168.1.1')

        r = http.get(PREFIX + '/host_info/123456789/00000090/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['hostnames'][0], 'hostname1')
        self.assertEqual(response['ip_addresses'][0], '192.168.1.1')

        r = http.get(PREFIX + '/host_info/123.456/00000090/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['hostnames'][0], 'hostname1')
        self.assertEqual(response['ip_addresses'][0], '192.168.1.1')

        r = http.get(PREFIX + '/host_info/-987654321/00000090/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['hostnames'][0], 'hostname1')
        self.assertEqual(response['ip_addresses'][0], '192.168.1.1')

        r = http.get(PREFIX + '/host_info/acceptable_chars_\@$-_.+!*\'(),^&~:;|}{}][]>=<>/00000090/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['hostnames'][0], 'hostname1')
        self.assertEqual(response['ip_addresses'][0], '192.168.1.1')

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/host_info//00000090/0001')

        self.assertEqual(ctx.exception.status, 404)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/host_info/bad_char?/00000090/0001')

        self.assertEqual(ctx.exception.status, 404)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/host_info/bad_char#/00000090/0001')

        self.assertEqual(ctx.exception.status, 404)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/host_info/bad_char%/00000090/0001')

        self.assertEqual(ctx.exception.status, 400)
