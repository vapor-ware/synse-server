#!/usr/bin/env python
"""
OpenDCRE Southbound API Device Read Tests
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


class DeviceReadTestCase(unittest.TestCase):
    """
        Test device read issues that may arise.
    """
    def test_001_read_zero(self):
        """
            Get a zero value for each supported conversion method
        """
        r = requests.get(PREFIX+"/read/thermistor/00000014/01FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        # self.assertEqual(response["device_raw"], 0)
        self.assertEqual(response["temperature_c"], 131.29)

        r = requests.get(PREFIX+"/read/humidity/00000014/02FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        # self.assertEqual(response["device_raw"], 0)
        self.assertEqual(response["temperature_c"], -40)
        self.assertEqual(response["humidity"], 0)

        r = requests.get(PREFIX+"/read/none/00000014/03FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_002_read_mid(self):
        """
            Get a midpoint value for each supported conversion method
        """
        r = requests.get(PREFIX+"/read/thermistor/00000014/04FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        # self.assertEqual(response["device_raw"], 32768)
        self.assertEqual(response["temperature_c"], -4173.97)

        r = requests.get(PREFIX+"/read/humidity/00000014/05FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        # self.assertEqual(response["device_raw"], 65535)            # 0x0000FFFF
        self.assertAlmostEqual(response["temperature_c"], 125, 1)  # max
        self.assertEqual(response["humidity"], 0)                  # zero

        r = requests.get(PREFIX+"/read/humidity/00000014/05FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        # self.assertEqual(response["device_raw"], 4294901760)     # 0xFFFF0000
        self.assertEqual(response["temperature_c"], -40)         # zero
        self.assertAlmostEqual(response["humidity"], 100, 1)     # max

        r = requests.get(PREFIX+"/read/none/00000014/06FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_003_read_8byte_max(self):
        """
            Get a max value for each supported conversion method
        """
        r = requests.get(PREFIX+"/read/thermistor/00000014/07FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)    # 65535 was the value

        r = requests.get(PREFIX+"/read/thermistor/00000014/08FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        # self.assertEqual(response["device_raw"], 65534)
        self.assertAlmostEqual(response["temperature_c"], -8466.32, 1)

        r = requests.get(PREFIX+"/read/humidity/00000014/09FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        # self.assertEqual(response["device_raw"], 4294967295)
        self.assertAlmostEqual(response["temperature_c"], 125, 1)
        self.assertAlmostEqual(response["humidity"], 100, 1)

        r = requests.get(PREFIX+"/read/none/00000014/0AFF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_004_weird_data(self):
        """
            What happens when a lot of integer data are returned?
        """
        r = requests.get(PREFIX+"/read/thermistor/00000014/0BFF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)    # we read something super weird for thermistor, so error

        r = requests.get(PREFIX+"/read/humidity/00000014/0CFF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)    # we read something super weird for humidity, so error

    def test_005_bad_data(self):
        """
            What happens when bad byte data are received.  What happens
            when there's a bad checksum or trailer?
        """
        # bad bytes
        r = requests.get(PREFIX+"/read/thermistor/00000014/0DFF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        # bad trailer
        r = requests.get(PREFIX+"/read/thermistor/00000014/0EFF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        # bad checksum
        r = requests.get(PREFIX+"/read/thermistor/00000014/0FFF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_006_no_data(self):
        """
            Timeout.
        """
        # timeout
        r = requests.get(PREFIX+"/read/none/00000014/10FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_006_board_id_representation(self):
        """
            Test reading while specifying different representations (same value) for
            the board id
        """
        r = requests.get(PREFIX+"/read/thermistor/14/04FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        # self.assertEqual(response["device_raw"], 32768)
        self.assertEqual(response["temperature_c"], -4173.97)

        r = requests.get(PREFIX+"/read/thermistor/014/04FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        # self.assertEqual(response["device_raw"], 32768)
        self.assertEqual(response["temperature_c"], -4173.97)

        r = requests.get(PREFIX+"/read/thermistor/00014/04FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        # self.assertEqual(response["device_raw"], 32768)
        self.assertEqual(response["temperature_c"], -4173.97)

        r = requests.get(PREFIX+"/read/thermistor/000014/04FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        # self.assertEqual(response["device_raw"], 32768)
        self.assertEqual(response["temperature_c"], -4173.97)

        r = requests.get(PREFIX+"/read/thermistor/00000014/04FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        # self.assertEqual(response["device_raw"], 32768)
        self.assertEqual(response["temperature_c"], -4173.97)

    def test_007_device_id_representation(self):
        """
            Test reading while specifying different representations (same value) for
            the device id
        """
        r = requests.get(PREFIX+"/read/thermistor/00000014/4FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        # self.assertEqual(response["device_raw"], 32768)
        self.assertEqual(response["temperature_c"], -4173.97)

        r = requests.get(PREFIX+"/read/thermistor/00000014/04FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        # self.assertEqual(response["device_raw"], 32768)
        self.assertEqual(response["temperature_c"], -4173.97)

        r = requests.get(PREFIX+"/read/thermistor/00000014/00004FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        # self.assertEqual(response["device_raw"], 32768)
        self.assertEqual(response["temperature_c"], -4173.97)

    def test_008_read_board_id_invalid(self):
        """
            Test read while specifying different invalid representations for
            the board id to ensure out-of-range values are not handled (e.g. set bits on packet that should not be set)
        """
        r = requests.get(PREFIX+"/read/thermistor/FFFFFFFF/1FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/read/thermistor/FFFFFFFFFFFFFFFF/1FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/read/thermistor/20000000/00001FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/read/thermistor/10000000/00001FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/read/thermistor/-10000000/00001FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/read/thermistor/-10000000/-00001FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/read/thermistor/10000000/-00001FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_009_read_temperature_valid(self):
        """
            Read a valid temperature value (30.03)
        """
        r = requests.get(PREFIX+"/read/temperature/00000015/0001", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 30.03)

    def test_010_read_temperature_invalid(self):
        """
            Read invalid temperature value (invalid)
        """
        r = requests.get(PREFIX+"/read/temperature/00000015/0002", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_011_read_temperature_float_string_valid(self):
        """
            Read a valid temperature value (30.03)
        """
        r = requests.get(PREFIX+"/read/temperature/00000015/0003", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 30.03)

    def test_012_read_temperature_int_string_valid(self):
        """
            Read a valid temperature value (30)
        """
        r = requests.get(PREFIX+"/read/temperature/00000015/0004", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 30)

    def test_013_read_temperature_int_valid(self):
        """
            Read a valid temperature value (30.03)
        """
        r = requests.get(PREFIX+"/read/temperature/00000015/0005", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 30)

