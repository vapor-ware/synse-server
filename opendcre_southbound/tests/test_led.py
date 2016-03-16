#!/usr/bin/env python
"""
OpenDCRE Southbound API Chassis LED Tests
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


class ChassisLedTestCase(unittest.TestCase):
    """
        Test fan speed reads and writes.
    """
    def test_001_read_on(self):
        """
            Read a valid on value back from led.
        """
        r = requests.get(PREFIX+"/read/led/00000030/0001", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["led_state"], 'on')

        r = requests.get(PREFIX+"/led/00000030/0001", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["led_state"], 'on')

    def test_002_read_off(self):
        """
            Read a valid off value back from led.
        """
        r = requests.get(PREFIX+"/read/led/00000030/0002", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["led_state"], 'off')

        r = requests.get(PREFIX+"/led/00000030/0002", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["led_state"], 'off')

    def test_003_read_invalid(self):
        """
            Read an empty data value, two integers and a string back from the led.
        """
        # empty
        r = requests.get(PREFIX+"/led/00000030/0003", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        # int 2
        r = requests.get(PREFIX+"/led/00000030/0003", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        # int 3
        r = requests.get(PREFIX+"/led/00000030/0003", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        # string "A"
        r = requests.get(PREFIX+"/led/00000030/0003", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        # empty
        r = requests.get(PREFIX+"/read/led/00000030/0003", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        # int 2
        r = requests.get(PREFIX+"/read/led/00000030/0003", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        # int 3
        r = requests.get(PREFIX+"/read/led/00000030/0003", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        # string "A"
        r = requests.get(PREFIX+"/read/led/00000030/0003", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_004_device_id_representation(self):
        """
            Test reading while specifying different representations (same value) for
            the device id
        """
        r = requests.get(PREFIX+"/read/led/00000030/000000001", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["led_state"], 'on')

        r = requests.get(PREFIX+"/led/00000030/000000001", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["led_state"], 'on')

    def test_005_read_board_id_invalid(self):
        """
            Test read while specifying different invalid representations for
            the board id to ensure out-of-range values are not handled (e.g. set bits on packet that should not be set)
        """
        r = requests.get(PREFIX+"/read/led/FFFFFFFF/1FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/read/led/FFFFFFFFFFFFFFFF/1FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/read/led/20000000/00001FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/read/led/10000000/00001FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/led/FFFFFFFF/1FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/led/FFFFFFFFFFFFFFFF/1FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/led/20000000/00001FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/led/10000000/00001FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/led/-10000000/00001FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_006_write_ok(self):
        """
            Test write with an ok response.
        """
        r = requests.get(PREFIX+"/led/00000030/0001/on", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)

        r = requests.get(PREFIX+"/led/00000030/0001/off", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)

    def test_007_write_not_ok(self):
        """
            Test write with a failed response.
        """
        r = requests.get(PREFIX+"/led/00000030/0002/on", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/led/00000030/0002/off", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_009_write_invalid_state(self):
        """
            Test write with invalid state values.
        """
        r = requests.get(PREFIX+"/led/00000030/0001/blinky", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/led/00000030/0001/1", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_012_write_with_bad_response(self):
        """
            Test write with bad responses.
        """
        # W2
        r = requests.get(PREFIX+"/led/00000030/0003/on", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        # W3
        r = requests.get(PREFIX+"/led/00000030/0003/on", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        # 1
        r = requests.get(PREFIX+"/led/00000030/0003/on", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        # 0
        r = requests.get(PREFIX+"/led/00000030/0003/on", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        # 2
        r = requests.get(PREFIX+"/led/00000030/0003/on", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)