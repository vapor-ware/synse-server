#!/usr/bin/env python
""" Test scanning when there is bad data for PLC.

    Author: Erick Daniszewski
    Date:   25 April 2017

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


class BadScanTestCase(unittest.TestCase):
    """ Test issuing scan command when the underlying data (in the emulator) is bad/
    corrupt, so devices will not register or scan correctly
    """

    def assert_scan_registration_failure(self, err_ctx):
        self.assertEqual(err_ctx.exception.status, 500)
        self.assertIn('not associated with any registered devicebus handler', err_ctx.exception.json['message'])

    def test_001_many_boards(self):
        """ Test for many boards (24 to be exact)
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/000000FF")
        self.assert_scan_registration_failure(ctx)

    def test_002_one_boards(self):
        """ Test for one board.
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/00000000")
        self.assert_scan_registration_failure(ctx)

    def test_003_no_boards(self):
        """ Test for no boards.
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/000000D2")
        self.assert_scan_registration_failure(ctx)

    def test_004_no_devices(self):
        """ Test for one board no devices.
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/00000001")
        self.assert_scan_registration_failure(ctx)

    def test_005_many_devices(self):
        """ Test for one board many devices.
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/00000002")
        self.assert_scan_registration_failure(ctx)

    def test_006_many_http(self):
        """ Test for one board many times.  Too many cooks.
        """
        for x in range(5):
            with self.assertRaises(VaporHTTPError) as ctx:
                http.get(PREFIX + "/scan/rack_1/00000000")
            self.assert_scan_registration_failure(ctx)

    def test_007_extraneous_data(self):
        """ Get a valid packet but with a boxload of data.
        We should be happy and drop the extra data on the floor.
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/00000003")
        self.assert_scan_registration_failure(ctx)

    def test_008_invalid_data(self):
        """ Get a valid packet but with bad data - checksum, trailer.
        """
        # BAD TRAILER
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/000000B4")
        self.assert_scan_registration_failure(ctx)

        # BAD CHECKSUM
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/000000BE")
        self.assert_scan_registration_failure(ctx)

    def test_009_no_data(self):
        """ Get no packet in return.
        """
        # TIMEOUT
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/0000C800")
        self.assert_scan_registration_failure(ctx)

    def test_010_bad_url(self):
        """ Get no packet in return.
        """
        # bad url
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/")

        self.assertEqual(ctx.exception.status, 404)

    def test_011_scan_bad_data(self):
        """ Test scanning all boards, where the list of boards/devices
        have either missing or malformed data. In this test, an
        incorrect response is expected.

        Here, we expect a 500 response because we intentionally have
        malformed data within the test json config being used. This
        means that when a scan is performed, the malformed data will
        get caught by the retry mechanism, and will ultimately fail
        (since retries will encounter the same corrupt values)
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/scan')

        self.assertEqual(ctx.exception.status, 500)

    def test_012_scan_board_id_representation(self):
        """ Test scanning while specifying different representations (same value) for
        the board id
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/3")
        self.assert_scan_registration_failure(ctx)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/03")
        self.assert_scan_registration_failure(ctx)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/003")
        self.assert_scan_registration_failure(ctx)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/0003")
        self.assert_scan_registration_failure(ctx)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/00003")
        self.assert_scan_registration_failure(ctx)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/000003")
        self.assert_scan_registration_failure(ctx)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/0000003")
        self.assert_scan_registration_failure(ctx)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/00000003")
        self.assert_scan_registration_failure(ctx)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/000000003")
        self.assert_scan_registration_failure(ctx)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/0000000003")
        self.assert_scan_registration_failure(ctx)

    def test_013_scan_board_id_invalid(self):
        """ Test scan while specifying different invalid representations for
        the board id to ensure out-of-range values are not handled (e.g. set bits
        on packet that should not be set)
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/FFFFFFFF")
        self.assert_scan_registration_failure(ctx)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/FFFFFFFFFFFFFFFF")
        self.assertEqual(ctx.exception.status, 500)
        self.assertIn('out of range', ctx.exception.json['message'])

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/20000000")
        self.assert_scan_registration_failure(ctx)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/10000000")
        self.assert_scan_registration_failure(ctx)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/-10000000")
        self.assertEqual(ctx.exception.status, 500)
        self.assertIn('out of range', ctx.exception.json['message'])

    def test_014_rack_id_representation(self):
        """ Test scan while specifying different values for the rack_id
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/00000000")
        self.assert_scan_registration_failure(ctx)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/STRING_NOT_RELATED_TO_RACK_AT_ALL/00000000")
        self.assert_scan_registration_failure(ctx)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/STRING WITH SPACES/00000000")
        self.assert_scan_registration_failure(ctx)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/123456789/00000000")
        self.assert_scan_registration_failure(ctx)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/123.456/00000000")
        self.assert_scan_registration_failure(ctx)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/-987654321/00000000")
        self.assert_scan_registration_failure(ctx)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/acceptable_chars_\@$-_.+!*'(),^&~:;|}{}][]>=<>/00000000")
        self.assert_scan_registration_failure(ctx)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan//00000000")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/bad_char?/00000000")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/bad_char#/00000000")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/bad_char%/00000000")

        self.assertEqual(ctx.exception.status, 400)
