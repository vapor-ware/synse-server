#!/usr/bin/env python
"""
OpenDCRE Location tests
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


class LocationTestCase(unittest.TestCase):
    """
        Test various location scenarios for boards and devices.
    """
    def test_001_valid_board_location(self):
        """
            Test simple location(valid board)
        """
        r = requests.get(PREFIX+"/location/00000000", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["physical_location"]["horizontal"], "unknown")
        self.assertEqual(response["physical_location"]["vertical"], "unknown")
        self.assertEqual(response["physical_location"]["depth"], "unknown")
        self.assertNotIn('chassis_location', response)

    def test_002_valid_board_device_location(self):
        """
            Test simple location (valid board, valid device)
        """
        r = requests.get(PREFIX+"/location/00000000/0000", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["physical_location"]["horizontal"], "unknown")
        self.assertEqual(response["physical_location"]["vertical"], "unknown")
        self.assertEqual(response["physical_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["horiz_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["vert_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["depth"], "unknown")

        r = requests.get(PREFIX+"/location/00000000/72DF", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["physical_location"]["horizontal"], "unknown")
        self.assertEqual(response["physical_location"]["vertical"], "unknown")
        self.assertEqual(response["physical_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["horiz_pos"], "left")
        self.assertEqual(response["chassis_location"]["vert_pos"], "bottom")
        self.assertEqual(response["chassis_location"]["depth"], "middle")
        self.assertEqual(response["chassis_location"]["server_node"], "unknown")

        r = requests.get(PREFIX+"/location/00000000/8302", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["physical_location"]["horizontal"], "unknown")
        self.assertEqual(response["physical_location"]["vertical"], "unknown")
        self.assertEqual(response["physical_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["horiz_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["vert_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["server_node"], 3)

        r = requests.get(PREFIX+"/location/00000000/5555", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["physical_location"]["horizontal"], "unknown")
        self.assertEqual(response["physical_location"]["vertical"], "unknown")
        self.assertEqual(response["physical_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["horiz_pos"], "left")
        self.assertEqual(response["chassis_location"]["vert_pos"], "top")
        self.assertEqual(response["chassis_location"]["depth"], "front")
        self.assertEqual(response["chassis_location"]["server_node"], 'unknown')

        r = requests.get(PREFIX+"/location/00000000/9F00", verify=SSL_CERT)
        self.assertEqual(r.status_code, 200)
        response = json.loads(r.text)
        self.assertEqual(response["physical_location"]["horizontal"], "unknown")
        self.assertEqual(response["physical_location"]["vertical"], "unknown")
        self.assertEqual(response["physical_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["horiz_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["vert_pos"], "unknown")
        self.assertEqual(response["chassis_location"]["depth"], "unknown")
        self.assertEqual(response["chassis_location"]["server_node"], 31)

    def test_003_invalid_board_location(self):
        """
            Test simple location (invalid board)
        """
        r = requests.get(PREFIX+"/location/80000000", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/location/8000000000", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/location/hot_dog", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/location/AAAAAAAA", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/location/-1", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

    def test_004_invalid_board_device_location(self):
        """
            Test simple location (valid board, invalid device)
        """
        r = requests.get(PREFIX+"/location/00000000/beer", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/location/00000000/F00DF00D", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/location/00000000/012345", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)

        r = requests.get(PREFIX+"/location/00000000/-01", verify=SSL_CERT)
        self.assertEqual(r.status_code, 500)


