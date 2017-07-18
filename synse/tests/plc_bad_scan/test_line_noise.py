#!/usr/bin/env python
""" Synse API Power Tests - Line Noise

    Author:  andrew
    Date:    12/4/2015

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


class LineNoiseTestCase(unittest.TestCase):
    """ Line Noise Tests - ignore junk at head, positive
    """

    def test_001_junk_head_scan(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/scan/rack_1/000000c8')

        self.assertEqual(ctx.exception.status, 500)
        self.assertIn('not associated with any registered devicebus handler', ctx.exception.json['message'])

    def test_004_junk_head_tooshort_scan(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/scan/rack_1/000000ca')

        self.assertEqual(ctx.exception.status, 500)
        self.assertIn('not associated with any registered devicebus handler', ctx.exception.json['message'])

    def test_007_junk_head_valid_long_scan(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/scan/rack_1/000000cc')

        self.assertEqual(ctx.exception.status, 500)
        self.assertIn('not associated with any registered devicebus handler', ctx.exception.json['message'])

    def test_010_junk_head_invalid_long_scan(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/scan/rack_1/000000ce')

        self.assertEqual(ctx.exception.status, 500)
        self.assertIn('not associated with any registered devicebus handler', ctx.exception.json['message'])

    def test_013_junk_head_junk_scan(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/scan/rack_1/000000d0')

        self.assertEqual(ctx.exception.status, 500)
        self.assertIn('not associated with any registered devicebus handler', ctx.exception.json['message'])
