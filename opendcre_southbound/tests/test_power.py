#!/usr/bin/env python
"""
OpenDCRE Southbound API Power Tests - NEW command syntax
Author:  andrew
Date:    1/23/2016

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


class PowerTestCase(unittest.TestCase):
    """
        Power control/status tests.
    """
    '''def test_000_no_auth(self):
        """
        Disabled as requires_auth removed.
        """
        # expect 401 status
        r = requests.get(PREFIX+"/power/0000001E/01FF/on", verify=SSL_CERT)
        self.assertEqual(r.status_code, 401)
    '''

    def test_001_get_power_status(self):
        # expected raw 0
        r = requests.get(PREFIX+"/power/0000001E/01FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)

        # reset the emulator to start at 0,0,0,0, or give up after 8 tries
        # (previous iterations of the old power tests leave the emulator mid-stream)
        i = 0
        while response['pmbus_raw'] != '0,0,0,0':
            r = requests.get(PREFIX+"/power/0000001E/01FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
            self.assertEqual(r.status_code, 200)
            response = json.loads(r.text)
            i += 1
            self.assertLess(i, 8)

        self.assertEqual(response["pmbus_raw"], "0,0,0,0")
        self.assertEqual(response["power_status"], "on")
        self.assertEqual(response["power_ok"], True)
        self.assertEqual(response["over_current"], False)
        self.assertEqual(response["under_voltage"], False)

        # expected raw 64 (0x40) - when off, power_ok and under_voltage
        # and under_current don't have any meaning
        r = requests.get(PREFIX+"/power/0000001E/01FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "64,0,0,0")
        self.assertEqual(response["power_status"], "off")
        self.assertEqual(response["power_ok"], True)
        self.assertEqual(response["over_current"], False)
        self.assertEqual(response["under_voltage"], False)

        # expected raw 2048 (0x800) - power problem but not
        # something related to under voltage or over current condition
        r = requests.get(PREFIX+"/power/0000001E/01FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2048,0,0,0")
        self.assertEqual(response["power_status"], "on")
        self.assertEqual(response["power_ok"], False)
        self.assertEqual(response["over_current"], False)
        self.assertEqual(response["under_voltage"], False)

        # expected raw 2048+8=2056 (0x1010) - power problem due to under voltage
        r = requests.get(PREFIX+"/power/0000001E/01FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2056,0,0,0")
        self.assertEqual(response["power_status"], "on")
        self.assertEqual(response["power_ok"], False)
        self.assertEqual(response["over_current"], False)
        self.assertEqual(response["under_voltage"], True)

        # expected raw 2048+16=2064 (0x1020) - power problem due to over current
        r = requests.get(PREFIX+"/power/0000001E/01FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2064,0,0,0")
        self.assertEqual(response["power_status"], "on")
        self.assertEqual(response["power_ok"], False)
        self.assertEqual(response["over_current"], True)
        self.assertEqual(response["under_voltage"], False)

        # expected raw 2072 (0x1030)
        r = requests.get(PREFIX+"/power/0000001E/01FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2072,0,0,0")
        self.assertEqual(response["power_status"], "on")
        self.assertEqual(response["power_ok"], False)
        self.assertEqual(response["over_current"], True)
        self.assertEqual(response["under_voltage"], True)

    def test_002_power_on(self):
        r = requests.get(PREFIX+"/power/0000001E/01FF/on", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)

    def test_003_power_cycle(self):
        r = requests.get(PREFIX+"/power/0000001E/01FF/cycle", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)

    def test_004_power_off(self):
        r = requests.get(PREFIX+"/power/0000001E/01FF/off", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)

    def test_005_valid_device_invalid_type(self):
        r = requests.get(PREFIX+"/power/0000001E/02FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_006_invalid_device(self):
        r = requests.get(PREFIX+"/power/0000001E/03FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_007_invalid_command(self):
        r = requests.get(PREFIX+"/power/0000001E/01FF/invalid", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/power/0000001E/01FF/cyle", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/power/0000001E/01FF/xxx", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_008_no_power_data(self):
        r = requests.get(PREFIX+"/power/0000001E/03FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/power/0000001E/04FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_010_weird_data(self):
        r = requests.get(PREFIX+"/power/0000001E/05FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/power/0000001E/06FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_011_power_board_id_representation(self):
        """
            Test power status while specifying different representations (same value) for
            the board id
        """
        r = requests.get(PREFIX+"/power/1E/01FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)

        r = requests.get(PREFIX+"/power/001E/01FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)

        r = requests.get(PREFIX+"/power/00001E/01FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)

        r = requests.get(PREFIX+"/power/0000000001E/01FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)

    def test_012_power_device_id_representation(self):
        """
            Test power status while specifying different representations (same value) for
            the board id
        """
        r = requests.get(PREFIX+"/power/0000001E/1FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)

        r = requests.get(PREFIX+"/power/0000001E/01FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)

        r = requests.get(PREFIX+"/power/0000001E/00001FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)

    def test_013_power_board_id_invalid(self):
        """
            Test power status while specifying different invalid representations for
            the board id to ensure out-of-range values are not handled (e.g. set bits on packet that should not be set)
        """
        r = requests.get(PREFIX+"/power/FFFFFFFF/1FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/power/FFFFFFFFFFFFFFFF/1FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/power/20000000/00001FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/power/10000000/00001FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/power/x/10000000/00001FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/power/-10000000/00001FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)