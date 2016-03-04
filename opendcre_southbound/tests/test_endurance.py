#!/usr/bin/env python
"""
OpenDCRE Southbound API Endurance Tests
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
import random

import requests

from test_config import PREFIX, SSL_CERT


# disable warnings for missing metadata from cert
# >> SecurityWarning: Certificate has no `subjectAltName`, falling back to check for a `commonName` for now. <<
requests.packages.urllib3.disable_warnings()


class EnduranceTestCase(unittest.TestCase):
    """
        Basic endurance tests.  Make sure there are not any lingering issues or
        clogged pipes between the bus and flask.
    """
    def test_001_random_good_requests(self):
        request_urls = [
            PREFIX+"/scan/00000001",
            PREFIX+"/version/00000001",
            PREFIX+"/read/thermistor/00000001/01FF",
            PREFIX+"/read/humidity/00000001/0CFF"
        ]
        for x in range(100):
            r = requests.get(request_urls[random.randint(0, len(request_urls)-1)], verify=SSL_CERT)
            self.assertEqual(r.status_code, 200)

    def test_002_device_reads(self):
        for x in range(100):
            r = requests.get(PREFIX+"/read/thermistor/00000001/01FF", verify=SSL_CERT)
            self.assertEqual(r.status_code, 200)
            r = requests.get(PREFIX+"/read/humidity/00000001/0CFF", verify=SSL_CERT)
            self.assertEqual(r.status_code, 200)
