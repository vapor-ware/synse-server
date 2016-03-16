#!/usr/bin/env python
"""
OpenDCRE Southbound API Device Scan Tests
Author:  andrew
Date:    4/13/2015
    \\//
     \/apor IO

Copyright (C) 2015-16  Vapor IO

This file is part of OpenDCRE.

OpenDCRE is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

OpenDCRE is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenDCRE.  If not, see <http://www.gnu.org/licenses/>.
"""
import unittest
import json
import requests

from test_config import PREFIX, SSL_CERT


# disable warnings for missing metadata from cert
# >> SecurityWarning: Certificate has no `subjectAltName`, falling back to check for a `commonName` for now. <<
requests.packages.urllib3.disable_warnings()


class ScanTestCase(unittest.TestCase):
    """
        Test board scan issues that may arise.
    """
    def test_001_many_boards(self):
        """
            Test for many boards (24 to be exact)
        """
        r = requests.get(PREFIX+"/scan/000000FF", verify=SSL_CERT)
        # response = json.loads(r.text)
        # self.assertEqual(len(response["boards"]), 24)
        self.assertEqual(r.status_code, 500)    # currently not enabled in firmware

    def test_002_one_boards(self):
        """
            Test for one board.
        """
        r = requests.get(PREFIX+"/scan/00000000", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(len(response["boards"]), 1)

    def test_003_no_boards(self):
        """
            Test for no boards.
        """
        r = requests.get(PREFIX+"/scan/000000D2", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_004_no_devices(self):
        """
            Test for one board no devices.
        """
        r = requests.get(PREFIX+"/scan/00000001", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)  # should this really be so?

    def test_005_many_devices(self):
        """
            Test for one board many devices.
        """
        r = requests.get(PREFIX+"/scan/00000002", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_006_many_requests(self):
        """
            Test for one board many times.  Too many cooks.
        """
        for x in range(5):
            r = requests.get(PREFIX+"/scan/00000000", verify=SSL_CERT)
            self.assertEqual(r.status_code, 200)
            response = json.loads(r.text)
            self.assertEqual(len(response["boards"]), 1)

    def test_007_extraneous_data(self):
        """
            Get a valid packet but with a boxload of data.
            We should be happy and drop the extra data on the floor.
        """
        r = requests.get(PREFIX+"/scan/00000003", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)

    def test_008_invalid_data(self):
        """
            Get a valid packet but with bad data - checksum, trailer.
        """
        # BAD TRAILER
        r = requests.get(PREFIX+"/scan/000000B4", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        # BAD CHECKSUM
        r = requests.get(PREFIX+"/scan/000000BE", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_009_no_data(self):
        """
            Get no packet in return.
        """
        # TIMEOUT
        r = requests.get(PREFIX+"/scan/0000C800", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_010_bad_url(self):
        """
            Get no packet in return.
        """
        # bad url
        r = requests.get(PREFIX+"/scan/", verify=SSL_CERT)
        self.assertEqual(r.status_code, 404)

    def test_011_scan_bad_data(self):
        """
            Test scanning all boards, where the list of boards/devices
            have either missing or malformed data. In this test, an
            incorrect response is expected.

            Here, we expect a 500 response because we intentionally have
            malformed data within the test json config being used. This
            means that when a scan is performed, the malformed data will
            get caught by the retry mechanism, and will ultimately fail
            (since retries will encounter the same corrupt values)
        """
        r = requests.get(PREFIX+'/scan', verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_012_scan_board_id_representation(self):
        """
            Test scanning while specifying different representations (same value) for
            the board id
        """
        r = requests.get(PREFIX+"/scan/3", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(len(response["boards"][0]["devices"]), 1)

        r = requests.get(PREFIX+"/scan/03", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(len(response["boards"][0]["devices"]), 1)

        r = requests.get(PREFIX+"/scan/003", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(len(response["boards"][0]["devices"]), 1)

        r = requests.get(PREFIX+"/scan/0003", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(len(response["boards"][0]["devices"]), 1)

        r = requests.get(PREFIX+"/scan/00003", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(len(response["boards"][0]["devices"]), 1)

        r = requests.get(PREFIX+"/scan/000003", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(len(response["boards"][0]["devices"]), 1)

        r = requests.get(PREFIX+"/scan/0000003", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(len(response["boards"][0]["devices"]), 1)

        r = requests.get(PREFIX+"/scan/00000003", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(len(response["boards"][0]["devices"]), 1)

        r = requests.get(PREFIX+"/scan/000000003", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(len(response["boards"][0]["devices"]), 1)

        r = requests.get(PREFIX+"/scan/0000000003", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(len(response["boards"][0]["devices"]), 1)

    def test_013_scan_board_id_invalid(self):
        """
            Test scan while specifying different invalid representations for
            the board id to ensure out-of-range values are not handled (e.g. set bits on packet that should not be set)
        """
        r = requests.get(PREFIX+"/scan/FFFFFFFF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/scan/FFFFFFFFFFFFFFFF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/scan/20000000", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/scan/10000000", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/scan/-10000000", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)
