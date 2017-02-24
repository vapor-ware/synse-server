#!/usr/bin/env python
""" OpenDCRE Southbound Redfish Endpoint Tests

    Author: Morgan Morley Mills, based off IPMI tests by Erick Daniszewski
    Date:   02/06/2017

    \\//
     \/apor IO

-------------------------------
Copyright (C) 2015-17  Vapor IO

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

from opendcre_southbound.tests.test_config import PREFIX
from vapor_common import http
from vapor_common.errors import VaporHTTPError

class RedfishBootTargetTestCase(unittest.TestCase):
    """ Test boot target reads and writes with the Redfish emulator running
    """
    def test_01_boot(self):
        """ Test the boot target endpoint in Redfish mode.
        """
        # setting the emulator from pxe to no_override:
        r = http.get(PREFIX + '/boot_target/rack_1/70000000/0200/no_override')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

        # checking that it is no_override:
        r = http.get(PREFIX + '/boot_target/rack_1/70000000/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

        # change boot target to hdd:
        r = http.get(PREFIX + '/boot_target/rack_1/70000000/0200/hdd')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'hdd')

        # checking that it is hdd:
        r = http.get(PREFIX + '/boot_target/rack_1/70000000/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'hdd')

        # change boot target to pxe:
        r = http.get(PREFIX + '/boot_target/rack_1/70000000/0200/pxe')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'pxe')

        # checking that boot target is pxe:
        r = http.get(PREFIX + '/boot_target/rack_1/70000000/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'pxe')

    def test_02_boot(self):
        """ Test the boot target endpoint in Redfish mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/70000000/0100')

    def test_03_boot(self):
        """ Test the boot target endpoint in Redfish mode.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/70000000/0200/invalid_target')

    def test_04_boot(self):
        """ Test the boot target endpoint in Redfish mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/70000000/0300')

    def test_05_boot(self):
        """ Test the boot target endpoint in Redfish mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/70000000/0001')

    def test_06_boot(self):
        """ Test the boot target endpoint in Redfish mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/70000000/0003')

    def test_07_boot(self):
        """ Test the boot target endpoint in Redfish mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/70000000/0005')

    def test_08_boot(self):
        """ Test the boot target endpoint in Redfish mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/70000000/0007')

    def test_09_boot(self):
        """ Test the boot target endpoint in Redfish mode.

        This should fail since we are attempting to set an invalid
        boot target.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/70000000/0012')

    def test_10_boot(self):
        """ Test the boot target endpoint in Redfish mode.
        """
        # setting the emulator from pxe to no_override:
        r = http.get(PREFIX + '/boot_target/rack_1/redfish-emulator/0200/no_override')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

        # checking that it is no_override:
        r = http.get(PREFIX + '/boot_target/rack_1/redfish-emulator/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

        # change boot target to hdd:
        r = http.get(PREFIX + '/boot_target/rack_1/redfish-emulator/0200/hdd')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'hdd')

        # checking that it is hdd:
        r = http.get(PREFIX + '/boot_target/rack_1/redfish-emulator/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'hdd')

        # change boot target to pxe:
        r = http.get(PREFIX + '/boot_target/rack_1/redfish-emulator/0200/pxe')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'pxe')

        # checking that boot target is pxe:
        r = http.get(PREFIX + '/boot_target/rack_1/redfish-emulator/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'pxe')

    def test_11_boot(self):
        """ Test the host info endpoint in Redfish mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/192.168.3.100/0200/no_override')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/test-3/0200/no_override')