#!/usr/bin/env python
"""
OpenDCRE Southbound API Device Bus Retry (line noise) Tests on Emulator

Author:  andrew
Date:    12/5/2015
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


class LineNoiseRetries(unittest.TestCase):
    """
        Test retry command (aka '?').
    """
    def test_001_single_read_retry_valid(self):
        """
            Single retry, valid retry response
        """
        r = requests.get(PREFIX+'/read/thermistor/10/01ff', verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        # self.assertEqual(response["device_raw"], 656)
        self.assertEqual(response["temperature_c"], 28.78)

    def test_002_single_power_retry_valid(self):
        """
            Single retry, valid retry response
        """
        r = requests.get(PREFIX+'/power/status/10/02ff', auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "0,0,0,0")

    def test_003_single_version_retry_valid(self):
        """
            Single retry, valid retry response
        """
        r = requests.get(PREFIX+'/version/10', verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["firmware_version"], "12345")

    def test_004_double_read_retry_valid(self):
        """
            Single retry, valid retry response
        """
        r = requests.get(PREFIX+'/read/thermistor/11/01ff', verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        # self.assertEqual(response["device_raw"], 656)
        self.assertEqual(response["temperature_c"], 28.78)

    def test_005_double_power_retry_valid(self):
        """
            Single retry, valid retry response
        """
        r = requests.get(PREFIX+'/power/status/11/02ff', auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "0,0,0,0")

    def test_006_double_version_retry_valid(self):
        """
            Single retry, valid retry response
        """
        r = requests.get(PREFIX+'/version/11', verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["firmware_version"], "12345")

    def test_007_triple_read_retry_valid(self):
        """
            Single retry, valid retry response
        """
        r = requests.get(PREFIX+'/read/thermistor/12/01ff', verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        # self.assertEqual(response["device_raw"], 656)
        self.assertEqual(response["temperature_c"], 28.78)

    def test_008_triple_power_retry_valid(self):
        """
            Single retry, valid retry response
        """
        r = requests.get(PREFIX+'/power/status/12/02ff', auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["pmbus_raw"], "0,0,0,0")

    def test_009_triple_version_retry_valid(self):
        """
            Single retry, valid retry response
        """
        r = requests.get(PREFIX+'/version/12', verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["firmware_version"], "12345")

    def test_010_triple_read_retry_fail(self):
        """
            Single retry, valid retry response
        """
        r = requests.get(PREFIX+'/read/thermistor/13/01ff', verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_011_triple_power_retry_fail(self):
        """
            Single retry, valid retry response
        """
        r = requests.get(PREFIX+'/power/status/13/02ff', auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_012_triple_version_retry_fail(self):
        """
            Single retry, valid retry response
        """
        r = requests.get(PREFIX+'/version/13', verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_013_triple_read_retry_fail(self):
        """
            Single retry, valid retry response
        """
        r = requests.get(PREFIX+'/read/thermistor/14/01ff', verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_014_triple_power_retry_fail(self):
        """
            Single retry, valid retry response
        """
        r = requests.get(PREFIX+'/power/status/14/02ff', auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_015_triple_version_retry_fail(self):
        """
            Single retry, valid retry response
        """
        r = requests.get(PREFIX+'/version/14', verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)
