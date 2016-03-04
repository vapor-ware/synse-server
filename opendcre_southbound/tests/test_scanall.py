#!/usr/bin/env python
"""
OpenDCRE Southbound API Scan-all Protocol Tests
Author:  andrew
Date:    2/28/2016
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


class ScanAllTestCase(unittest.TestCase):
    """
        Test board scan all, with various results.
    """
    def test_001_scan_all_ok(self):
        """
            Test expecting ok results (10 boards)
        """
        r = requests.get(PREFIX+"/scan", verify=SSL_CERT)
        response = json.loads(r.text)
        self.assertEqual(len(response["boards"]), 10)
        self.assertEqual(r.status_code, 200)

    def test_002_scan_all_fail(self):
        """
            Test expecting failed results (error, error, error --> 500)
        """
        r = requests.get(PREFIX+"/scan", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_003_scan_all_two_bad_ok(self):
        """
            Test expecting ok results (10 boards)
        """
        r = requests.get(PREFIX+"/scan", verify=SSL_CERT)
        response = json.loads(r.text)
        self.assertEqual(len(response["boards"]), 10)
        self.assertEqual(r.status_code, 200)

    def test_004_scan_all_one_bad_ok(self):
        """
            Test expecting ok results (10 boards)
        """
        r = requests.get(PREFIX+"/scan", verify=SSL_CERT)
        response = json.loads(r.text)
        self.assertEqual(len(response["boards"]), 10)
        self.assertEqual(r.status_code, 200)

    def test_005_scan_all_error_then_read(self):
        """
            Test expecting failed results (error, error, error --> 500)
        """
        r = requests.get(PREFIX+"/scan", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/read/temperature/00000002/2000")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response['temperature_c'], 28.78)

    def test_006_scan_all_error_then_scan_board(self):
        """
            Test expecting failed results (error, error, error --> 500)
        """
        r = requests.get(PREFIX+"/scan", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/scan/00000001")
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(len(response["boards"]), 1)
        self.assertEqual(len(response["boards"][0]['devices']), 2)