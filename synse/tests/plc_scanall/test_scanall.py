#!/usr/bin/env python
""" Synse API Scan-all Protocol Tests

    Author:  andrew
    Date:    2/28/2016

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

from vapor_common import http


class ScanAllTestCase(unittest.TestCase):
    """ Test board scan all, with various results.
    """

    def test_001_scan_all_ok(self):
        """ Test expecting ok results (10 boards)
        """
        r = http.get(PREFIX + "/scan/force")
        response = r.json()
        self.assertTrue(http.request_ok(r.status_code))
        self.assertEqual(len(response['racks'][0]["boards"]), 10)

    '''
    def test_002_scan_all_fail(self):
        """ Test expecting failed results (error, error, error --> 500)
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/force")

        self.assertEqual(ctx.exception.status, 500)
        print ctx.exception.json

    def test_003_scan_all_two_bad_ok(self):
        """ Test expecting ok results (10 boards)
        """
        r = http.get(PREFIX + "/scan/force")
        response = r.json()
        self.assertEqual(len(response['racks'][0]["boards"]), 10)
        self.assertTrue(http.request_ok(r.status_code))

    def test_004_scan_all_one_bad_ok(self):
        """ Test expecting ok results (10 boards)
        """
        r = http.get(PREFIX + "/scan/force")
        response = r.json()
        self.assertEqual(len(response['racks'][0]['boards']), 10)
        self.assertTrue(http.request_ok(r.status_code))

    def test_005_scan_all_error_then_read(self):
        """ Test expecting failed results (error, error, error --> 500)
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/force")

        self.assertEqual(ctx.exception.status, 500)
        print ctx.exception.json

        r = http.get(PREFIX + "/read/temperature/rack_1/00000002/2000")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 28.78)

    def test_006_scan_all_error_then_scan_board(self):
        """ Test expecting failed results (error, error, error --> 500)
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/force")

        self.assertEqual(ctx.exception.status, 500)
        print ctx.exception.json

        r = http.get(PREFIX + "/scan/rack_1/00000001")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(len(response["boards"]), 1)
        self.assertEqual(len(response["boards"][0]['devices']), 2)
    '''
