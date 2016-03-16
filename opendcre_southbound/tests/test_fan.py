#!/usr/bin/env python
"""
OpenDCRE Southbound API Fan Speed Tests
Author:  andrew
Date:    2/23/2016
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


class FanSpeedTestCase(unittest.TestCase):
    """
        Test fan speed reads and writes.
    """
    def test_001_read_ok(self):
        """
            Read a valid value back from fan.
        """
        r = requests.get(PREFIX+"/read/fan_speed/00000028/0001", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["speed_rpm"], 4100)

        r = requests.get(PREFIX+"/fan/00000028/0001", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["speed_rpm"], 4100)

    def test_002_read_string(self):
        """
            Read a string value back from fan (negative).
        """
        r = requests.get(PREFIX+"/read/fan_speed/00000028/0002", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/fan/00000028/0002", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_003_read_empty(self):
        """
            Read an empty data value back from the fan.
        """
        r = requests.get(PREFIX+"/read/fan_speed/00000028/0003", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/fan/00000028/0003", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_004_long_value(self):
        """
            What happens when a large integer is returned? (positive)
        """
        r = requests.get(PREFIX+"/read/fan_speed/00000028/0004", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["speed_rpm"], 12345678901234567890)

        r = requests.get(PREFIX+"/fan/00000028/0004", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["speed_rpm"], 12345678901234567890)

    def test_005_negative_number(self):
        """
            What happens when a negative number is returned? (positive)
        """
        r = requests.get(PREFIX+"/read/fan_speed/00000028/0005", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["speed_rpm"], -12345)

        r = requests.get(PREFIX+"/fan/00000028/0005", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["speed_rpm"], -12345)

    def test_006_device_id_representation(self):
        """
            Test reading while specifying different representations (same value) for
            the device id
        """
        r = requests.get(PREFIX+"/read/fan_speed/00000028/000000001", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["speed_rpm"], 4100)

        r = requests.get(PREFIX+"/fan/00000028/000000001", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["speed_rpm"], 4100)

    def test_007_read_board_id_invalid(self):
        """
            Test read while specifying different invalid representations for
            the board id to ensure out-of-range values are not handled (e.g. set bits on packet that should not be set)
        """
        r = requests.get(PREFIX+"/read/fan_speed/FFFFFFFF/1FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/read/fan_speed/FFFFFFFFFFFFFFFF/1FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/read/fan_speed/20000000/00001FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/read/fan_speed/10000000/00001FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/fan/FFFFFFFF/1FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/fan/FFFFFFFFFFFFFFFF/1FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/fan/20000000/00001FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/fan/10000000/00001FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_008_write_ok(self):
        """
            Test write with an ok response.
        """
        r = requests.get(PREFIX+"/fan/00000028/0001/4100", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)

    def test_009_write_long(self):
        """
            Test write with long numbers.
        """
        r = requests.get(PREFIX+"/fan/00000028/0001/00000000004100", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)

        r = requests.get(PREFIX+"/fan/00000028/0001/12345678901234567890", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_010_write_neg_num(self):
        """
            Test write with negative numbers.
        """
        r = requests.get(PREFIX+"/fan/00000028/0001/-4100", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_011_write_string(self):
        """
            Test write with string.
        """
        r = requests.get(PREFIX+"/fan/00000028/0001/faster", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_012_write_bad_board(self):
        """
            Test write with bad board.
        """
        r = requests.get(PREFIX+"/fan/00000029/0001/4100", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/fan/-00000029/0001/4100", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_013_write_bad_device(self):
        """
            Test write with bad device.
        """
        r = requests.get(PREFIX+"/fan/00000028/00FF/4100", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/fan/00000028/-00FF/4100", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_012_write_with_bad_response(self):
        """
            Test write with bad response.
        """
        r = requests.get(PREFIX+"/fan/00000028/0002/4100", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)


