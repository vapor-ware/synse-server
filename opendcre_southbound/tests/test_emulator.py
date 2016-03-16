#!/usr/bin/env python
"""
OpenDCRE Southbound API Device Bus Emulator Tests
Author:  erick
Date:    8/25/2015
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


class EmulatorCounterTestCase(unittest.TestCase):
    """
        Tests to ensure the emulator counter behaves as is expected and does
        not get changed erroneously.
    """
    def test_001_read_same_board_same_device(self):
        """
            Test reading a single thermistor device repeatedly to make sure it
            increments sequentially.
        """
        r = requests.get(PREFIX+"/read/temperature/00000001/01FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 100)

        r = requests.get(PREFIX+"/read/temperature/00000001/01FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 101)

        r = requests.get(PREFIX+"/read/temperature/00000001/01FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 102)

    def test_002_read_same_board_diff_device(self):
        """
            Test reading thermistor devices on the same board but different devices,
            where both devices have the same length of responses and repeatable=true.
            One device being tested does not start at the first response since
            previous tests have incremented its counter.
        """
        r = requests.get(PREFIX+"/read/temperature/00000001/01FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 103)

        r = requests.get(PREFIX+"/read/temperature/00000001/03FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 200)

        r = requests.get(PREFIX+"/read/temperature/00000001/01FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 104)

        r = requests.get(PREFIX+"/read/temperature/00000001/03FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 201)

    def test_003_read_diff_board_diff_device(self):
        """
            Test reading thermistor devices on different boards, where both
            devices have the same length of responses and repeatable=true. One
            device being tested does not start at the first response since
            previous tests have incremented its counter.
        """
        r = requests.get(PREFIX+"/read/temperature/00000001/03FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 202)

        r = requests.get(PREFIX+"/read/temperature/00000003/02FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 800)

        r = requests.get(PREFIX+"/read/temperature/00000001/03FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 203)

        r = requests.get(PREFIX+"/read/temperature/00000003/02FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 801)

    def test_004_read_until_wraparound(self):
        """
            Test incrementing the counter on alternating devices (humidity
            and thermistor), both where repeatable=true, but where the length
            of the responses list differ.
        """
        r = requests.get(PREFIX+"/read/temperature/00000001/0CFF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 600)

        r = requests.get(PREFIX+"/read/temperature/00000001/0AFF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 500)

        r = requests.get(PREFIX+"/read/temperature/00000001/0CFF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 601)

        r = requests.get(PREFIX+"/read/temperature/00000001/0AFF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 501)

        r = requests.get(PREFIX+"/read/temperature/00000001/0CFF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 602)

        r = requests.get(PREFIX+"/read/temperature/00000001/0AFF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 502)

        r = requests.get(PREFIX+"/read/temperature/00000001/0CFF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 603)

        r = requests.get(PREFIX+"/read/temperature/00000001/0AFF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 503)

        # counter should wrap back around here, since len(responses) has
        # been exceeded.
        r = requests.get(PREFIX+"/read/temperature/00000001/0CFF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 600)

        # counter should not wrap around for this device, since len(responses)
        # has not been exceeded
        r = requests.get(PREFIX+"/read/temperature/00000001/0AFF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 504)

        r = requests.get(PREFIX+"/read/temperature/00000001/0CFF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 601)

        r = requests.get(PREFIX+"/read/temperature/00000001/0AFF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 505)

    def test_005_power_same_board_diff_device(self):
        """
            Test incrementing the counter on alternating power devices,
            one where repeatable=true, and one where repeatable=false
        """
        r = requests.get(PREFIX+"/power/status/00000001/06FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "0,0,0,0")

        r = requests.get(PREFIX+"/power/status/00000001/07FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "0,0,0,0")

        r = requests.get(PREFIX+"/power/status/00000001/06FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "64,0,0,0")

        r = requests.get(PREFIX+"/power/status/00000001/07FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "64,0,0,0")

        r = requests.get(PREFIX+"/power/status/00000001/06FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2048,0,0,0")

        r = requests.get(PREFIX+"/power/status/00000001/07FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2048,0,0,0")

        # repeatable=true, so the counter should cycle back around
        r = requests.get(PREFIX+"/power/status/00000001/06FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "0,0,0,0")

        # repeatable=false, so should not the counter back around
        r = requests.get(PREFIX+"/power/status/00000001/07FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_006_power_read_alternation(self):
        """
           Test incrementing the counter alternating between a power cmd and
           a read cmd, both where repeatable=true.
        """
        # perform three requests on the thermistor to get the count different from
        # the start count of the power
        r = requests.get(PREFIX+"/read/temperature/00000001/08FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 300)

        r = requests.get(PREFIX+"/read/temperature/00000001/08FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 301)

        r = requests.get(PREFIX+"/read/temperature/00000001/08FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 302)

        # start alternating between power and thermistor
        r = requests.get(PREFIX+"/power/status/00000001/05FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "0,0,0,0")

        r = requests.get(PREFIX+"/read/temperature/00000001/08FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 303)

        r = requests.get(PREFIX+"/power/status/00000001/05FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "64,0,0,0")

        r = requests.get(PREFIX+"/read/temperature/00000001/08FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 304)

        r = requests.get(PREFIX+"/power/status/00000001/05FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2048,0,0,0")

        r = requests.get(PREFIX+"/read/temperature/00000001/08FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 305)

        r = requests.get(PREFIX+"/power/status/00000001/05FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "2056,0,0,0")

        r = requests.get(PREFIX+"/read/temperature/00000001/08FF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["temperature_c"], 306)
