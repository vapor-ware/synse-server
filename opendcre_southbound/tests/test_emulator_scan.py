#!/usr/bin/env python
"""
OpenDCRE Southbound API Device Bus Scan Tests on Emulator

NOTE: these tests might (and perhaps should) belong in the "devicebus" test
suite, but because that test suite uses intentionally invalid board/device
values for the tests, scan all will not work correctly and will give back
hokey data. These tests are to ensure correct scan all behavior.

Author:  erick
Date:    10/22/2015
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

from test_config import PREFIX


# disable warnings for missing metadata from cert
# >> SecurityWarning: Certificate has no `subjectAltName`, falling back to check for a `commonName` for now. <<
requests.packages.urllib3.disable_warnings()


class ScanAllTestCase(unittest.TestCase):
    """
        Tests to ensure scan all board functionality works
    """
    def test_001_scan_all_boards(self):
        """
            Test to scan all boards
        """
        r = requests.get(PREFIX+'/scan')
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(len(response["boards"]), 8)

        expected_board_ids = ['00000001', '00000003', '00000010', '00000011', '00000012', '00000013', '00000014', '12345678']
        for board in response['boards']:
            self.assertIn(board['board_id'], expected_board_ids)

    def test_002_scan_boards_individually(self):
        """
            Test scanning each board individually
        """
        r = requests.get(PREFIX+'/scan/00000001')
        self.assertEqual(r.status_code, 200)

        r = requests.get(PREFIX+'/scan/00000003')
        self.assertEqual(r.status_code, 200)

        r = requests.get(PREFIX+'/scan/00000010')
        self.assertEqual(r.status_code, 200)

        # removed case below as sequence number is hardcoded, and
        # already utilized in case 001 above.
        #r = requests.get(PREFIX+'/scan/12345678')
        #self.assertEqual(r.status_code, 200)

    def test_003_scan_nonexistent_boards(self):
        """
            Test scanning boards individually for boards that do not exist
        """
        r = requests.get(PREFIX+'/scan/0000000A')
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+'/scan/004920A6')
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+'/scan/00654321')
        self.assertEqual(r.status_code, 500)
