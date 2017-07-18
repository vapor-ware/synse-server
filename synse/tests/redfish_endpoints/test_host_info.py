#!/usr/bin/env python
""" Synse Redfish Endpoint Tests

    Author: Morgan Morley Mills, based off IPMI tests by Erick Daniszewski
    Date:   02/06/2017

    \\//
     \/apor IO

-------------------------------
Copyright (C) 2015-17  Vapor IO

This file is part of Synse.

Synse is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

Synse is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Synse.  If not, see <http://www.gnu.org/licenses/>.
"""
import unittest

from synse.vapor_common import http
from synse.vapor_common.errors import VaporHTTPError

from synse.tests.test_config import PREFIX


class RedfishHostInfoTestCase(unittest.TestCase):
    """ Test host info reads with the Redfish emulator running
    """
    def test_01_hostinfo(self):
        """ Test the asset endpoint in Redfish mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/70000000/0100')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 1)
        self.assertEqual(ip_addresses[0], 'redfish-emulator')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 1)

    def test_02_hostinfo(self):
        """ Test the host info endpoint in Redfish mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/70000000/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 1)
        self.assertEqual(ip_addresses[0], 'redfish-emulator')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 1)

    def test_03_hostinfo(self):
        """ Test the host info endpoint in Redfish mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/70000000/0300')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 1)
        self.assertEqual(ip_addresses[0], 'redfish-emulator')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 1)

    def test_04_hostinfo(self):
        """ Test the host info endpoint in Redfish mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/70000000/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 1)
        self.assertEqual(ip_addresses[0], 'redfish-emulator')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 1)

    def test_05_hostinfo(self):
        """ Test the host info endpoint in Redfish mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/70000000/0003')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 1)
        self.assertEqual(ip_addresses[0], 'redfish-emulator')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 1)

    def test_06_hostinfo(self):
        """ Test the host info endpoint in Redfish mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/70000000/0005')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 1)
        self.assertEqual(ip_addresses[0], 'redfish-emulator')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 1)

    def test_07_hostinfo(self):
        """ Test the host info endpoint in Redfish mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/70000000/0007')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 1)
        self.assertEqual(ip_addresses[0], 'redfish-emulator')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 1)

    def test_08_hostinfo(self):
        """ Test the host info endpoint in Redfish mode.

        In this case, the given device id does not exist, but host info for
        Redfish does not check device id, so it should still return a valid response.
        """
        r = http.get(PREFIX + '/host_info/rack_1/70000000/0056')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 1)
        self.assertEqual(ip_addresses[0], 'redfish-emulator')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 1)

    def test_09_hostinfo(self):
        """ Test the host info endpoint in Redfish mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/host_info/rack_1/40654321/0001')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/host_info/rack_1/192.168.3.100/0100')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/host_info/rack_1/test-3/0100')

    def test_10_hostinfo(self):
        """ Test the host info endpoint in Redfish mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/redfish-emulator/0100')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 1)
        self.assertEqual(ip_addresses[0], 'redfish-emulator')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 1)

    def test_11_hostinfo(self):
        """ Test the host info endpoint in Redfish mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/redfish-emulator/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 1)
        self.assertEqual(ip_addresses[0], 'redfish-emulator')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 1)
