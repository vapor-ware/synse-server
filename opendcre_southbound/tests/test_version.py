#!/usr/bin/env python
"""
OpenDCRE Southbound API Version Tests
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


class VersionTestCase(unittest.TestCase):
    """
        Test board version issues that may arise.
    """
    def test_001_simple_version(self):
        """
            Test simple version (valid board, valid version)
        """
        r = requests.get(PREFIX+"/version/0000000A", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["firmware_version"], "Version Response 1")

    def test_002_very_long_version(self):
        """
            Test long version (valid board, valid version)
            Technically > 32 bytes will split stuff into multiple
            packets.
        """
        r = requests.get(PREFIX+"/version/0000000B", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_003_empty_version(self):
        """
            Test empty version (valid board, empty version)
        """
        r = requests.get(PREFIX+"/version/0000000C", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["firmware_version"], "")

    def test_004_many_board_versions(self):
        """
            Test many board versions (valid boards, various versions)
        """
        for x in range(5):
            r = requests.get(PREFIX+"/version/"+"{0:08x}".format(x+13), verify=SSL_CERT)
            self.assertEqual(r.status_code, 200)
            response = json.loads(r.text)
            self.assertEqual(response["firmware_version"], "Version 0x0"+str(x+1))

    def test_005_long_data(self):
        """
            Data > 32 bytes (should be multiple packets but we cheat currently)
        """
        r = requests.get(PREFIX+"/version/00000012", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["firmware_version"], "0123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789")

    def test_006_bad_data(self):
        """
            Bad checksum, bad trailer.
        """
        # bad trailer
        r = requests.get(PREFIX+"/version/000000B5", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        # bad checksum
        r = requests.get(PREFIX+"/version/000000BF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_007_no_data(self):
        """
            Timeout.
        """
        # timeout
        r = requests.get(PREFIX+"/version/0000C800", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_008_bad_url(self):
        """
            Timeout.
        """
        # bad url
        r = requests.get(PREFIX+"/version/", verify=SSL_CERT)
        self.assertEqual(r.status_code, 404)

    def test_009_device_id_representation(self):
        """
            Test version while specifying different representations (same value) for
            the device id
        """
        r = requests.get(PREFIX+"/version/A", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["firmware_version"], "Version Response 1")

        r = requests.get(PREFIX+"/version/00A", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["firmware_version"], "Version Response 1")

        r = requests.get(PREFIX+"/version/00000A", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["firmware_version"], "Version Response 1")

        r = requests.get(PREFIX+"/version/000000000A", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["firmware_version"], "Version Response 1")

        r = requests.get(PREFIX+"/version/00000000000000000A", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["firmware_version"], "Version Response 1")

    def test_010_invalid_board_id(self):
        """
            Test version while specifying invalid board_id representation.
        """
        r = requests.get(PREFIX+"/version/-1", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)
