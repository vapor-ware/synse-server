#!/usr/bin/env python
""" Synse IPMI Device Registration Tests

    Author: Erick Daniszewski
    Date:   10/26/2016

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

from synse.tests.test_config import PREFIX


class IPMIDeviceRegistrationTestCase(unittest.TestCase):
    """ Simple test against Synse IPMI threaded device registration. With multiple
    threads enabled and multiple BMCs defined (3 BMCs on rack 1, 1 BMC on rack 2 for
    this test), we should be able to test the full capabilities of the threaded registration.
    This can be validated by looking at the scan results to ensure all devices are present.
    """

    def test_001_test_scan(self):
        """ Test the Synse scan endpoint.
        """
        r = http.get(PREFIX + '/scan', timeout=30)
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('racks', response)

        racks = response['racks']
        self.assertIsInstance(racks, list)
        self.assertEqual(len(racks), 2)

        # rack 1 - we expect there to be 3 BMCs registered for this rack
        rack = [i for i in racks if i['rack_id'] == 'rack_1']
        self.assertEqual(len(rack), 1)
        rack = rack[0]

        self.assertIsInstance(rack, dict)
        self.assertIn('rack_id', rack)
        self.assertIn('boards', rack)

        boards = rack['boards']
        self.assertIsInstance(boards, list)
        self.assertEqual(len(boards), 3)

        for board in boards:
            self.assertIsInstance(board, dict)
            self.assertIn('board_id', board)
            self.assertIn('ip_addresses', board)
            self.assertIn('hostnames', board)
            self.assertIn('devices', board)
            for ip_addr in board['ip_addresses']:
                self.assertIn(ip_addr, [
                    'ipmi-emulator-1',
                    'ipmi-emulator-2',
                    'ipmi-emulator-3'
                ])

            devices = board['devices']
            self.assertIsInstance(devices, list)
            self.assertEqual(len(devices), 16)

            device_types = [
                'power', 'system', 'led', 'voltage', 'fan_speed', 'temperature', 'power_supply'
            ]

            for device in devices:
                self.assertIsInstance(device, dict)
                self.assertIn('device_type', device)
                self.assertIn('device_id', device)

                dev_type = device['device_type']
                self.assertIn(dev_type.lower(), device_types)

        # rack 2 - we expect there to be 1 BMC registered for this rack
        rack = [i for i in racks if i['rack_id'] == 'rack_2']
        self.assertEqual(len(rack), 1)
        rack = rack[0]

        self.assertIsInstance(rack, dict)
        self.assertIn('rack_id', rack)
        self.assertIn('boards', rack)

        boards = rack['boards']
        self.assertIsInstance(boards, list)
        self.assertEqual(len(boards), 1)

        for board in boards:
            self.assertIsInstance(board, dict)
            self.assertIn('board_id', board)
            self.assertIn('ip_addresses', board)
            self.assertIn('hostnames', board)
            self.assertIn('devices', board)
            for ip_addr in board['ip_addresses']:
                self.assertIn(ip_addr, [
                    'ipmi-emulator-4'
                ])

            devices = board['devices']
            self.assertIsInstance(devices, list)
            self.assertEqual(len(devices), 16)

            device_types = [
                'power', 'system', 'led', 'voltage', 'fan_speed', 'temperature', 'power_supply'
            ]

            for device in devices:
                self.assertIsInstance(device, dict)
                self.assertIn('device_type', device)
                self.assertIn('device_id', device)

                dev_type = device['device_type']
                self.assertIn(dev_type.lower(), device_types)
