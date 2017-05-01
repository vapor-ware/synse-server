#!/usr/bin/env python
""" OpenDCRE Southbound IPMI Device Registration Tests

    Author: Erick Daniszewski
    Date:   10/26/2016

    \\//
     \/apor IO
"""
import unittest

from opendcre_southbound.tests.test_config import PREFIX
from vapor_common import http


class IPMIDeviceRegistrationTestCase(unittest.TestCase):
    """ Simple test against OpenDCRE IPMI threaded device registration. With multiple
    threads enabled and multiple BMCs defined (3 BMCs on rack 1, 1 BMC on rack 2 for
    this test), we should be able to test the full capabilities of the threaded registration.
    This can be validated by looking at the scan results to ensure all devices are present.
    """

    def test_001_test_scan(self):
        """ Test the OpenDCRE scan endpoint.
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
