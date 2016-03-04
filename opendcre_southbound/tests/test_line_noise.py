#!/usr/bin/env python
"""
OpenDCRE Southbound API Power Tests - Line Noise
Author:  andrew
Date:    12/4/2015
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
from requests.auth import HTTPBasicAuth

from test_config import PREFIX, TEST_USERNAME, TEST_PASSWORD, SSL_CERT


# disable warnings for missing metadata from cert
# >> SecurityWarning: Certificate has no `subjectAltName`, falling back to check for a `commonName` for now. <<
requests.packages.urllib3.disable_warnings()


class LineNoiseTestCase(unittest.TestCase):
    """
        Line Noise Tests - ignore junk at head, positive
    """
    def test_000_junk_head_scan(self):
        # expect 200 status, single thermistor
        r = requests.get(PREFIX+"/scan/000000c8", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["boards"][0]["board_id"], "00000002")
        self.assertEqual(response["boards"][0]["devices"][0]["device_id"], "01ff")
        self.assertEqual(response["boards"][0]["devices"][0]["device_type"], "thermistor")

    def test_001_junk_head_version(self):
        # expect 200 status, version string
        r = requests.get(PREFIX+"/version/000000c9", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["firmware_version"], "12345")

    def test_002_junk_head_read(self):
        # expect 200 status, thermistor reading
        r = requests.get(PREFIX+"/read/thermistor/000000c9/01ff", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        # self.assertEqual(response["device_raw"], 656)
        self.assertEqual(response["temperature_c"], 28.78)

    """
        Line Noise Tests - ignore junk at head, packet too short, all neg
    """
    def test_003_junk_head_tooshort_scan(self):
        # expect 500 status
        r = requests.get(PREFIX+"/scan/000000ca", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_004_junk_head_tooshort_version(self):
        # expect 500 status
        r = requests.get(PREFIX+"/version/000000cb", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_005_junk_head_tooshort_read(self):
        # expect 500 status
        r = requests.get(PREFIX+"/read/thermistor/000000cb/01ff", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)
    """
        Line Noise Tests - ignore junk at head, valid packet with junk at tail, positive
    """
    def test_006_junk_head_valid_long_scan(self):
        # expect 200 status, single thermistor
        r = requests.get(PREFIX+"/scan/000000cc", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["boards"][0]["board_id"], "00000002")
        self.assertEqual(response["boards"][0]["devices"][0]["device_id"], "01ff")
        self.assertEqual(response["boards"][0]["devices"][0]["device_type"], "thermistor")

    def test_007_junk_head_valid_long_version(self):
        # expect 200 status, version string
        r = requests.get(PREFIX+"/version/000000cd", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["firmware_version"], "12345")

    def test_008_junk_head_valid_long_read(self):
        # expect 200 status, thermistor reading
        r = requests.get(PREFIX+"/read/thermistor/000000cd/01ff", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        # self.assertEqual(response["device_raw"], 656)
        self.assertEqual(response["temperature_c"], 28.78)
    """
        Line Noise Tests - ignore junk at head, invalid packet, junk at end, negative
    """
    def test_009_junk_head_invalid_long_scan(self):
        # expect 500 status
        r = requests.get(PREFIX+"/scan/000000ce", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_010_junk_head_invalid_long_version(self):
        # expect 500 status
        r = requests.get(PREFIX+"/version/000000cf", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_011_junk_head_invalid_long_read(self):
        # expect 500 status
        r = requests.get(PREFIX+"/read/thermistor/000000cf/01ff", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)
    """
        Line Noise Tests - junk packet, no header, all negative
    """
    def test_012_junk_head_junk_scan(self):
        # expect 500 status, single thermistor
        r = requests.get(PREFIX+"/scan/000000d0", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_013_junk_head_junk_version(self):
        # expect 500 status
        r = requests.get(PREFIX+"/version/000000d1", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_014_junk_head_junk_read(self):
        # expect 500 status
        r = requests.get(PREFIX+"/read/thermistor/000000d1/01ff", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
