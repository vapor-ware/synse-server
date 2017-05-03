#!/usr/bin/env python
""" VaporCORE Southbound API Device Bus Scan Tests on Emulator

NOTE: these tests might (and perhaps should) belong in the "devicebus" test
suite, but because that test suite uses intentionally invalid board/device
values for the tests, scan all will not work correctly and will give back
hokey data. These tests are to ensure correct scan all behavior.

    Author:  Erick Daniszewski
    Date:    10/22/2015

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


class ScanAllTestCase(unittest.TestCase):
    """ Tests to ensure scan all board functionality works
    """
    def test_001_scan_all_boards(self):
        """ Test to scan all boards
        """
        r = http.get(PREFIX + '/scan')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()

        # NOTE: while the emulator data file, data/emulator-data.json, has 8 boards
        # defined, one of the boards does not contain any devices. the board is still
        # recognized internally, but the REST API will omit boards without devices, so
        # we expect to not see that board here.
        self.assertEqual(len(response['racks'][0]['boards']), 7)

        expected_board_ids = ['00000001', '00000003', '00000010', '00000011', '00000012', '00000013', '00000014']
        for board in response['racks'][0]['boards']:
            self.assertIn(board['board_id'], expected_board_ids)

    def test_002_scan_boards_individually(self):
        """ Test scanning each board individually
        """
        r = http.get(PREFIX + '/scan/rack_1/00000001')
        self.assertTrue(http.request_ok(r.status_code))

        r = http.get(PREFIX + '/scan/rack_1/00000003')
        self.assertTrue(http.request_ok(r.status_code))

        r = http.get(PREFIX + '/scan/rack_1/00000010')
        self.assertTrue(http.request_ok(r.status_code))

    def test_003_scan_nonexistent_boards(self):
        """ Test scanning boards individually for boards that do not exist
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/scan/rack_1/0000000A')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/scan/rack_1/004920A6')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/scan/rack_1/00654321')

        self.assertEqual(ctx.exception.status, 500)
