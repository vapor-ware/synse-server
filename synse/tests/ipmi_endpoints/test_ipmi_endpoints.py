#!/usr/bin/env python
""" Synse IPMI Endpoint Tests

    Author: Erick Daniszewski
    Date:   09/27/2016

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

from synse.version import __api_version__
from synse.tests.test_config import PREFIX

from vapor_common import http
from vapor_common.errors import VaporHTTPError


class IPMIEndpointsTestCase(unittest.TestCase):
    """ IPMI Endpoint tests test hitting Synse endpoints with only an IPMI
    device configured, with the IPMI emulator running.
    """

    def test_000_test_endpoint(self):
        """ Hit the Synse 'test' endpoint to verify that it is running.
        """
        r = http.get(PREFIX + '/test')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertEqual(response['status'], 'ok')

    def test_001_test_endpoint(self):
        """ Hit the Synse 'test' endpoint to verify that it is running.
        """
        r = http.post(PREFIX + '/test')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertEqual(response['status'], 'ok')

    def test_002_version_endpoint(self):
        """ Hit the Synse versionless version endpoint to verify it is
        running the correct API version.
        """
        # remove the last 4 chars (the api version) from the prefix as this endpoint
        # is version-less.
        r = http.get(PREFIX[:-4] + '/version')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertEqual(response['version'], __api_version__)

    def test_003_version_endpoint(self):
        """ Hit the Synse versionless version endpoint to verify it is
        running the correct API version.
        """
        # remove the last 4 chars (the api version) from the prefix as this endpoint
        # is version-less.
        r = http.post(PREFIX[:-4] + '/version')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertEqual(response['version'], __api_version__)

    def test_004_test_scan_all(self):
        """ Test the Synse scan all endpoint.
        """
        r = http.get(PREFIX + '/scan')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('racks', response)

        racks = response['racks']
        self.assertIsInstance(racks, list)
        self.assertEqual(len(racks), 1)

        rack = racks[0]
        self.assertIsInstance(rack, dict)
        self.assertIn('rack_id', rack)
        self.assertEqual(rack['rack_id'], 'rack_1')
        self.assertIn('boards', rack)

        boards = rack['boards']
        self.assertIsInstance(boards, list)
        self.assertEqual(len(boards), 1)

        board = boards[0]
        self.assertIsInstance(board, dict)
        self.assertIn('board_id', board)
        self.assertEqual(board['board_id'], '40000000')
        self.assertIn('ip_addresses', board)
        self.assertEqual(board['ip_addresses'], ['192.168.1.100', '192.168.2.100', '192.168.1.100'])
        self.assertIn('hostnames', board)
        self.assertEqual(board['hostnames'], ['test-1', 'test-2', 'test-1'])
        self.assertIn('devices', board)

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

    def test_005_test_force_scan_all(self):
        """ Test the Synse force scan endpoint.
        """
        r = http.get(PREFIX + '/scan/force')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('racks', response)

        racks = response['racks']
        self.assertIsInstance(racks, list)
        self.assertEqual(len(racks), 1)

        rack = racks[0]
        self.assertIsInstance(rack, dict)
        self.assertIn('rack_id', rack)
        self.assertEqual(rack['rack_id'], 'rack_1')
        self.assertIn('boards', rack)

        boards = rack['boards']
        self.assertIsInstance(boards, list)
        self.assertEqual(len(boards), 1)

        board = boards[0]
        self.assertIsInstance(board, dict)
        self.assertIn('board_id', board)
        self.assertEqual(board['board_id'], '40000000')
        self.assertIn('ip_addresses', board)
        self.assertEqual(board['ip_addresses'], ['192.168.1.100', '192.168.2.100', '192.168.1.100'])
        self.assertIn('hostnames', board)
        self.assertEqual(board['hostnames'], ['test-1', 'test-2', 'test-1'])
        self.assertIn('devices', board)

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

    def test_006_test_scan(self):
        """ Test the Synse scan rack endpoint.
        """
        r = http.get(PREFIX + '/scan/rack_1')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('racks', response)

        racks = response['racks']
        self.assertIsInstance(racks, list)
        self.assertEqual(len(racks), 1)

        rack = racks[0]
        self.assertIsInstance(rack, dict)
        self.assertIn('rack_id', rack)
        self.assertEqual(rack['rack_id'], 'rack_1')
        self.assertIn('boards', rack)

        boards = rack['boards']
        self.assertIsInstance(boards, list)
        self.assertEqual(len(boards), 1)

        board = boards[0]
        self.assertIsInstance(board, dict)
        self.assertIn('board_id', board)
        self.assertEqual(board['board_id'], '40000000')
        self.assertIn('ip_addresses', board)
        self.assertEqual(board['ip_addresses'], ['192.168.1.100', '192.168.2.100', '192.168.1.100'])
        self.assertIn('hostnames', board)
        self.assertEqual(board['hostnames'], ['test-1', 'test-2', 'test-1'])
        self.assertIn('devices', board)

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

    def test_007_test_scan(self):
        """ Test the Synse scan board endpoint.
        """
        r = http.get(PREFIX + '/scan/rack_1/40000000')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('boards', response)

        boards = response['boards']
        self.assertIsInstance(boards, list)
        self.assertEqual(len(boards), 1)

        board = boards[0]
        self.assertIsInstance(board, dict)
        self.assertIn('board_id', board)
        self.assertEqual(board['board_id'], '40000000')
        self.assertIn('ip_addresses', board)
        self.assertEqual(board['ip_addresses'], ['192.168.1.100', '192.168.2.100', '192.168.1.100'])
        self.assertIn('hostnames', board)
        self.assertEqual(board['hostnames'], ['test-1', 'test-2', 'test-1'])
        self.assertIn('devices', board)

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

    def test_008_read(self):
        """ Test reading an IPMI device.

        This should fail since 'power' is unsupported for ipmi reads.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/rack_1/power/40000000/0100')

    def test_009_read(self):
        """ Test reading an IPMI device.

        This should fail since 'system' is unsupported for ipmi reads.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/rack_1/system/40000000/0200')

    def test_010_read(self):
        """ Test reading an IPMI device.

        This should fail since 'led' is unsupported for ipmi reads.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/led/rack_1/40000000/0300')

    def test_011_read(self):
        """ Test reading an IPMI device.
        """
        r = http.get(PREFIX + '/read/voltage/rack_1/40000000/0021')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('voltage', response)
        self.assertIsInstance(response['voltage'], float)

    def test_012_read(self):
        """ Test reading an IPMI device.
        """
        r = http.get(PREFIX + '/read/fan_speed/rack_1/40000000/0042')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('speed_rpm', response)
        self.assertIsInstance(response['speed_rpm'], float)
        self.assertEqual(response['speed_rpm'], 3915)

    def test_013_read(self):
        """ Test reading an IPMI device.
        """
        r = http.get(PREFIX + '/read/voltage/rack_1/40000000/0023')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('voltage', response)
        self.assertIsInstance(response['voltage'], float)

    def test_014_read(self):
        """ Test reading an IPMI device.
        """
        r = http.get(PREFIX + '/read/voltage/rack_1/40000000/0024')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('voltage', response)
        self.assertIsInstance(response['voltage'], float)

    def test_015_read(self):
        """ Test reading an IPMI device.
        """
        r = http.get(PREFIX + '/read/voltage/rack_1/40000000/0025')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('voltage', response)
        self.assertIsInstance(response['voltage'], float)

    def test_016_read(self):
        """ Test reading an IPMI device.
        """
        r = http.get(PREFIX + '/read/voltage/rack_1/40000000/0026')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('voltage', response)
        self.assertIsInstance(response['voltage'], float)

    def test_017_read(self):
        """ Test reading an IPMI device.

        This should fail since the fan device is not 'present' in the emulator.
        """
        r = http.get(PREFIX + '/read/fan_speed/rack_1/40000000/0041')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('speed_rpm', response)
        self.assertIsInstance(response['speed_rpm'], float)

    def test_018_read(self):
        """ Test reading an IPMI device.
        """
        r = http.get(PREFIX + '/read/voltage/rack_1/40000000/0028')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('voltage', response)
        self.assertIsInstance(response['voltage'], float)

    def test_019_read(self):
        """ Test reading an IPMI device.
        """
        r = http.get(PREFIX + '/read/voltage/rack_1/40000000/0027')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('voltage', response)
        self.assertIsInstance(response['voltage'], float)

    def test_020_read(self):
        """ Test reading an IPMI device.
        """
        r = http.get(PREFIX + '/read/voltage/rack_1/40000000/0022')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('voltage', response)
        self.assertIsInstance(response['voltage'], float)

    def test_021_read(self):
        """ Test reading an IPMI device.
        """
        r = http.get(PREFIX + '/read/temperature/rack_1/40000000/0011')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)

    def test_022_read(self):
        """ Test reading an IPMI device.
        """
        r = http.get(PREFIX + '/read/temperature/rack_1/40000000/0012')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)

    def test_023_power(self):
        """ Test power control with IPMI.

        This will turn the power off to test reads when the BMC in unpowered.
        In these cases, we expect that the reads should not return data.
        """
        r = http.get(PREFIX + '/power/rack_1/40000000/0100/off')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'off')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertEqual(response['input_power'], 0)

    def test_024_read(self):
        """ Test reading an IPMI device.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/voltage/rack_1/40000000/0021')

    def test_025_read(self):
        """ Test reading an IPMI device.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/fan_speed/rack_1/40000000/0042')

    def test_026_read(self):
        """ Test reading an IPMI device.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/voltage/rack_1/40000000/0023')

    def test_027_read(self):
        """ Test reading an IPMI device.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/voltage/rack_1/40000000/0024')

    def test_028_read(self):
        """ Test reading an IPMI device.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/voltage/rack_1/40000000/0025')

    def test_029_read(self):
        """ Test reading an IPMI device.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/voltage/rack_1/40000000/0026')

    def test_030_read(self):
        """ Test reading an IPMI device.

        This should fail since the fan device is not 'present' in the emulator.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/fan_speed/rack_1/40000000/0041')

    def test_031_read(self):
        """ Test reading an IPMI device.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/voltage/rack_1/40000000/0028')

    def test_032_read(self):
        """ Test reading an IPMI device.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/voltage/rack_1/40000000/0027')

    def test_033_read(self):
        """ Test reading an IPMI device.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/voltage/rack_1/40000000/0022')

    def test_034_read(self):
        """ Test reading an IPMI device.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/temperature/rack_1/40000000/0011')

    def test_035_read(self):
        """ Test reading an IPMI device.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/temperature/rack_1/40000000/0012')

    def test_036_power(self):
        """ Test power control with IPMI.
        """
        r = http.get(PREFIX + '/power/rack_1/40000000/0100/on')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertTrue(150 <= response['input_power'] <= 250)

    def test_037_power(self):
        """ Test power control with IPMI.
        """
        r = http.get(PREFIX + '/power/rack_1/40000000/0100')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertTrue(150 <= response['input_power'] <= 250)

    def test_038_power(self):
        """ Test power control with IPMI.
        """
        r = http.get(PREFIX + '/power/rack_1/40000000/0100/status')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertTrue(150 <= response['input_power'] <= 250)

    def test_039_power(self):
        """ Test power control with IPMI.
        """
        r = http.get(PREFIX + '/power/rack_1/40000000/0100')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertTrue(150 <= response['input_power'] <= 250)

        r = http.get(PREFIX + '/power/rack_1/40000000/0100/off')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'off')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertEqual(response['input_power'], 0)

        r = http.get(PREFIX + '/power/rack_1/40000000/0100')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'off')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertEqual(response['input_power'], 0)

        r = http.get(PREFIX + '/power/rack_1/40000000/0100/on')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertTrue(150 <= response['input_power'] <= 250)

        r = http.get(PREFIX + '/power/rack_1/40000000/0100')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertTrue(150 <= response['input_power'] <= 250)

    def test_040_power(self):
        """ Test power control with IPMI.

        This should fail since the specified action is invalid.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/power/rack_1/40000000/0100/not-an-action')

    def test_041_asset(self):
        """ Test the asset endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/40000000/0100')

    def test_042_asset(self):
        """ Test the asset endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/asset/rack_1/40000000/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)

        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)

        self.assertIn('bmc_ip', response)
        bmc_ip = response['bmc_ip']
        self.assertEqual(bmc_ip, 'ipmi-emulator')  # name passed thru the cfg file which is the emulator container name

        self.assertIn('product_info', response)
        product_info = response['product_info']
        self.assertIsInstance(product_info, dict)
        for item in ['asset_tag', 'part_number', 'version', 'serial_number', 'product_name', 'manufacturer']:
            self.assertIn(item, product_info)

        self.assertIn('board_info', response)
        board_info = response['board_info']
        self.assertIsInstance(board_info, dict)
        for item in ['serial_number', 'part_number', 'product_name', 'manufacturer']:
            self.assertIn(item, board_info)

        self.assertIn('chassis_info', response)
        chassis_info = response['chassis_info']
        self.assertIsInstance(chassis_info, dict)
        for item in ['serial_number', 'part_number', 'chassis_type']:
            self.assertIn(item, chassis_info)

    def test_043_asset(self):
        """ Test the asset endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/40000000/0300')

    def test_044_asset(self):
        """ Test the asset endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/40000000/0021')

    def test_045_asset(self):
        """ Test the asset endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/40000000/0042')

    def test_046_asset(self):
        """ Test the asset endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/40000000/0023')

    def test_047_asset(self):
        """ Test the asset endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/40000000/0024')

    def test_048_asset(self):
        """ Test the asset endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/40000000/0025')

    def test_049_asset(self):
        """ Test the asset endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/40000000/0026')

    def test_050_asset(self):
        """ Test the asset endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/40000000/0041')

    def test_051_asset(self):
        """ Test the asset endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/40000000/0028')

    def test_052_asset(self):
        """ Test the asset endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/40000000/0027')

    def test_053_asset(self):
        """ Test the asset endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/40000000/0022')

    def test_054_asset(self):
        """ Test the asset endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/40000000/0011')

    def test_055_asset(self):
        """ Test the asset endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/40000000/0012')

    def test_056_asset(self):
        """ Test the asset endpoint in IPMI mode.

        Tests getting asset info of a board that does not exist
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/40654321/0012')

    def test_057_asset(self):
        """ Test the asset endpoint in IPMI mode.

        Tests getting asset info of a device that does not exist
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/40000000/abcd')

    def test_058_boot_target(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/40000000/0100')

    def test_059_boot_target(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/boot_target/rack_1/40000000/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

        r = http.get(PREFIX + '/boot_target/rack_1/40000000/0200/pxe')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'pxe')

        r = http.get(PREFIX + '/boot_target/rack_1/40000000/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'pxe')

        r = http.get(PREFIX + '/boot_target/rack_1/40000000/0200/hdd')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/rack_1/40000000/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/rack_1/40000000/0200/no_override')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

        r = http.get(PREFIX + '/boot_target/rack_1/40000000/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

    def test_060_boot_target(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/40000000/0200/invalid_target')

    def test_061_boot_target(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/40000000/0300')

    def test_062_boot_target(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/40000000/0021')

    def test_063_boot_target(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/40000000/0042')

    def test_064_boot_target(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/40000000/0023')

    def test_065_boot_target(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/40000000/0024')

    def test_066_boot_target(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/40000000/0025')

    def test_067_boot_target(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/40000000/0026')

    def test_068_boot_target(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/40000000/0041')

    def test_069_boot_target(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/40000000/0028')

    def test_070_boot_target(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/40000000/0027')

    def test_071_boot_target(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/40000000/0022')

    def test_072_boot_target(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/40000000/0011')

    def test_073_boot_target(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/40000000/0012')

    def test_074_boot_target(self):
        """ Test the boot target endpoint in IPMI mode.

        This should fail since we are attempting to set an invalid
        boot target.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/40000000/0012')

    def test_075_location(self):
        """ Test getting location information in IPMI mode.
        """
        r = http.get(PREFIX + '/location/rack_1/40000000')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 2)
        self.assertIn('request_received', response)
        self.assertIn('physical_location', response)

        physical_location = response['physical_location']
        self.assertIsInstance(physical_location, dict)
        self.assertEqual(len(physical_location), 3)
        self.assertIn('depth', physical_location)
        self.assertIn('horizontal', physical_location)
        self.assertIn('vertical', physical_location)
        self.assertEqual(physical_location['depth'], 'unknown')
        self.assertEqual(physical_location['horizontal'], 'unknown')
        self.assertEqual(physical_location['vertical'], 'unknown')

    def test_076_location(self):
        """ Test getting location information in IPMI mode.

        In this test, the provided board does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/location/rack_1/40654321')

    def test_077_location(self):
        """ Test the location endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/location/rack_1/40000000/0100')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 3)
        self.assertIn('physical_location', response)
        self.assertIn('chassis_location', response)
        self.assertIn('request_received', response)

        physical_location = response['physical_location']
        self.assertIsInstance(physical_location, dict)
        self.assertEqual(len(physical_location), 3)
        self.assertIn('depth', physical_location)
        self.assertIn('horizontal', physical_location)
        self.assertIn('vertical', physical_location)
        self.assertEqual(physical_location['depth'], 'unknown')
        self.assertEqual(physical_location['horizontal'], 'unknown')
        self.assertEqual(physical_location['vertical'], 'unknown')

        chassis_location = response['chassis_location']
        self.assertIsInstance(chassis_location, dict)
        self.assertEqual(len(chassis_location), 4)
        self.assertIn('depth', chassis_location)
        self.assertIn('server_node', chassis_location)
        self.assertIn('horiz_pos', chassis_location)
        self.assertIn('vert_pos', chassis_location)
        self.assertEqual(chassis_location['depth'], 'unknown')
        self.assertEqual(chassis_location['server_node'], 'unknown')
        self.assertEqual(chassis_location['horiz_pos'], 'unknown')
        self.assertEqual(chassis_location['vert_pos'], 'unknown')

    def test_078_location(self):
        """ Test the location endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/location/rack_1/40000000/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 3)
        self.assertIn('physical_location', response)
        self.assertIn('chassis_location', response)
        self.assertIn('request_received', response)

        physical_location = response['physical_location']
        self.assertIsInstance(physical_location, dict)
        self.assertEqual(len(physical_location), 3)
        self.assertIn('depth', physical_location)
        self.assertIn('horizontal', physical_location)
        self.assertIn('vertical', physical_location)
        self.assertEqual(physical_location['depth'], 'unknown')
        self.assertEqual(physical_location['horizontal'], 'unknown')
        self.assertEqual(physical_location['vertical'], 'unknown')

        chassis_location = response['chassis_location']
        self.assertIsInstance(chassis_location, dict)
        self.assertEqual(len(chassis_location), 4)
        self.assertIn('depth', chassis_location)
        self.assertIn('server_node', chassis_location)
        self.assertIn('horiz_pos', chassis_location)
        self.assertIn('vert_pos', chassis_location)
        self.assertEqual(chassis_location['depth'], 'unknown')
        self.assertEqual(chassis_location['server_node'], 'unknown')
        self.assertEqual(chassis_location['horiz_pos'], 'unknown')
        self.assertEqual(chassis_location['vert_pos'], 'bottom')

    def test_079_location(self):
        """ Test the location endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/location/rack_1/40000000/0300')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 3)
        self.assertIn('physical_location', response)
        self.assertIn('chassis_location', response)
        self.assertIn('request_received', response)

        physical_location = response['physical_location']
        self.assertIsInstance(physical_location, dict)
        self.assertEqual(len(physical_location), 3)
        self.assertIn('depth', physical_location)
        self.assertIn('horizontal', physical_location)
        self.assertIn('vertical', physical_location)
        self.assertEqual(physical_location['depth'], 'unknown')
        self.assertEqual(physical_location['horizontal'], 'unknown')
        self.assertEqual(physical_location['vertical'], 'unknown')

        chassis_location = response['chassis_location']
        self.assertIsInstance(chassis_location, dict)
        self.assertEqual(len(chassis_location), 4)
        self.assertIn('depth', chassis_location)
        self.assertIn('server_node', chassis_location)
        self.assertIn('horiz_pos', chassis_location)
        self.assertIn('vert_pos', chassis_location)
        self.assertEqual(chassis_location['depth'], 'unknown')
        self.assertEqual(chassis_location['server_node'], 'unknown')
        self.assertEqual(chassis_location['horiz_pos'], 'unknown')
        self.assertEqual(chassis_location['vert_pos'], 'bottom')

    def test_080_location(self):
        """ Test the location endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/location/rack_1/40000000/0021')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 3)
        self.assertIn('physical_location', response)
        self.assertIn('chassis_location', response)
        self.assertIn('request_received', response)

        physical_location = response['physical_location']
        self.assertIsInstance(physical_location, dict)
        self.assertEqual(len(physical_location), 3)
        self.assertIn('depth', physical_location)
        self.assertIn('horizontal', physical_location)
        self.assertIn('vertical', physical_location)
        self.assertEqual(physical_location['depth'], 'unknown')
        self.assertEqual(physical_location['horizontal'], 'unknown')
        self.assertEqual(physical_location['vertical'], 'unknown')

        chassis_location = response['chassis_location']
        self.assertIsInstance(chassis_location, dict)
        self.assertEqual(len(chassis_location), 4)
        self.assertIn('depth', chassis_location)
        self.assertIn('server_node', chassis_location)
        self.assertIn('horiz_pos', chassis_location)
        self.assertIn('vert_pos', chassis_location)
        self.assertEqual(chassis_location['depth'], 'unknown')
        self.assertEqual(chassis_location['server_node'], 'unknown')
        self.assertEqual(chassis_location['horiz_pos'], 'unknown')
        self.assertEqual(chassis_location['vert_pos'], 'unknown')

    def test_081_location(self):
        """ Test the location endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/location/rack_1/40000000/0042')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 3)
        self.assertIn('physical_location', response)
        self.assertIn('chassis_location', response)
        self.assertIn('request_received', response)

        physical_location = response['physical_location']
        self.assertIsInstance(physical_location, dict)
        self.assertEqual(len(physical_location), 3)
        self.assertIn('depth', physical_location)
        self.assertIn('horizontal', physical_location)
        self.assertIn('vertical', physical_location)
        self.assertEqual(physical_location['depth'], 'unknown')
        self.assertEqual(physical_location['horizontal'], 'unknown')
        self.assertEqual(physical_location['vertical'], 'unknown')

        chassis_location = response['chassis_location']
        self.assertIsInstance(chassis_location, dict)
        self.assertEqual(len(chassis_location), 4)
        self.assertIn('depth', chassis_location)
        self.assertIn('server_node', chassis_location)
        self.assertIn('horiz_pos', chassis_location)
        self.assertIn('vert_pos', chassis_location)
        self.assertEqual(chassis_location['depth'], 'unknown')
        self.assertEqual(chassis_location['server_node'], 'unknown')
        self.assertEqual(chassis_location['horiz_pos'], 'unknown')
        self.assertEqual(chassis_location['vert_pos'], 'unknown')

    def test_082_location(self):
        """ Test the location endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/location/rack_1/40000000/0023')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 3)
        self.assertIn('physical_location', response)
        self.assertIn('chassis_location', response)
        self.assertIn('request_received', response)

        physical_location = response['physical_location']
        self.assertIsInstance(physical_location, dict)
        self.assertEqual(len(physical_location), 3)
        self.assertIn('depth', physical_location)
        self.assertIn('horizontal', physical_location)
        self.assertIn('vertical', physical_location)
        self.assertEqual(physical_location['depth'], 'unknown')
        self.assertEqual(physical_location['horizontal'], 'unknown')
        self.assertEqual(physical_location['vertical'], 'unknown')

        chassis_location = response['chassis_location']
        self.assertIsInstance(chassis_location, dict)
        self.assertEqual(len(chassis_location), 4)
        self.assertIn('depth', chassis_location)
        self.assertIn('server_node', chassis_location)
        self.assertIn('horiz_pos', chassis_location)
        self.assertIn('vert_pos', chassis_location)
        self.assertEqual(chassis_location['depth'], 'unknown')
        self.assertEqual(chassis_location['server_node'], 'unknown')
        self.assertEqual(chassis_location['horiz_pos'], 'unknown')
        self.assertEqual(chassis_location['vert_pos'], 'unknown')

    def test_083_location(self):
        """ Test the location endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/location/rack_1/40000000/0024')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 3)
        self.assertIn('physical_location', response)
        self.assertIn('chassis_location', response)
        self.assertIn('request_received', response)

        physical_location = response['physical_location']
        self.assertIsInstance(physical_location, dict)
        self.assertEqual(len(physical_location), 3)
        self.assertIn('depth', physical_location)
        self.assertIn('horizontal', physical_location)
        self.assertIn('vertical', physical_location)
        self.assertEqual(physical_location['depth'], 'unknown')
        self.assertEqual(physical_location['horizontal'], 'unknown')
        self.assertEqual(physical_location['vertical'], 'unknown')

        chassis_location = response['chassis_location']
        self.assertIsInstance(chassis_location, dict)
        self.assertEqual(len(chassis_location), 4)
        self.assertIn('depth', chassis_location)
        self.assertIn('server_node', chassis_location)
        self.assertIn('horiz_pos', chassis_location)
        self.assertIn('vert_pos', chassis_location)
        self.assertEqual(chassis_location['depth'], 'unknown')
        self.assertEqual(chassis_location['server_node'], 'unknown')
        self.assertEqual(chassis_location['horiz_pos'], 'unknown')
        self.assertEqual(chassis_location['vert_pos'], 'unknown')

    def test_084_location(self):
        """ Test the location endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/location/rack_1/40000000/0025')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 3)
        self.assertIn('physical_location', response)
        self.assertIn('chassis_location', response)
        self.assertIn('request_received', response)

        physical_location = response['physical_location']
        self.assertIsInstance(physical_location, dict)
        self.assertEqual(len(physical_location), 3)
        self.assertIn('depth', physical_location)
        self.assertIn('horizontal', physical_location)
        self.assertIn('vertical', physical_location)
        self.assertEqual(physical_location['depth'], 'unknown')
        self.assertEqual(physical_location['horizontal'], 'unknown')
        self.assertEqual(physical_location['vertical'], 'unknown')

        chassis_location = response['chassis_location']
        self.assertIsInstance(chassis_location, dict)
        self.assertEqual(len(chassis_location), 4)
        self.assertIn('depth', chassis_location)
        self.assertIn('server_node', chassis_location)
        self.assertIn('horiz_pos', chassis_location)
        self.assertIn('vert_pos', chassis_location)
        self.assertEqual(chassis_location['depth'], 'unknown')
        self.assertEqual(chassis_location['server_node'], 'unknown')
        self.assertEqual(chassis_location['horiz_pos'], 'unknown')
        self.assertEqual(chassis_location['vert_pos'], 'unknown')

    def test_085_location(self):
        """ Test the location endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/location/rack_1/40000000/0026')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 3)
        self.assertIn('physical_location', response)
        self.assertIn('chassis_location', response)
        self.assertIn('request_received', response)

        physical_location = response['physical_location']
        self.assertIsInstance(physical_location, dict)
        self.assertEqual(len(physical_location), 3)
        self.assertIn('depth', physical_location)
        self.assertIn('horizontal', physical_location)
        self.assertIn('vertical', physical_location)
        self.assertEqual(physical_location['depth'], 'unknown')
        self.assertEqual(physical_location['horizontal'], 'unknown')
        self.assertEqual(physical_location['vertical'], 'unknown')

        chassis_location = response['chassis_location']
        self.assertIsInstance(chassis_location, dict)
        self.assertEqual(len(chassis_location), 4)
        self.assertIn('depth', chassis_location)
        self.assertIn('server_node', chassis_location)
        self.assertIn('horiz_pos', chassis_location)
        self.assertIn('vert_pos', chassis_location)
        self.assertEqual(chassis_location['depth'], 'unknown')
        self.assertEqual(chassis_location['server_node'], 'unknown')
        self.assertEqual(chassis_location['horiz_pos'], 'unknown')
        self.assertEqual(chassis_location['vert_pos'], 'unknown')

    def test_086_location(self):
        """ Test the location endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/location/rack_1/40000000/0041')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 3)
        self.assertIn('physical_location', response)
        self.assertIn('chassis_location', response)
        self.assertIn('request_received', response)

        physical_location = response['physical_location']
        self.assertIsInstance(physical_location, dict)
        self.assertEqual(len(physical_location), 3)
        self.assertIn('depth', physical_location)
        self.assertIn('horizontal', physical_location)
        self.assertIn('vertical', physical_location)
        self.assertEqual(physical_location['depth'], 'unknown')
        self.assertEqual(physical_location['horizontal'], 'unknown')
        self.assertEqual(physical_location['vertical'], 'unknown')

        chassis_location = response['chassis_location']
        self.assertIsInstance(chassis_location, dict)
        self.assertEqual(len(chassis_location), 4)
        self.assertIn('depth', chassis_location)
        self.assertIn('server_node', chassis_location)
        self.assertIn('horiz_pos', chassis_location)
        self.assertIn('vert_pos', chassis_location)
        self.assertEqual(chassis_location['depth'], 'unknown')
        self.assertEqual(chassis_location['server_node'], 'unknown')
        self.assertEqual(chassis_location['horiz_pos'], 'unknown')
        self.assertEqual(chassis_location['vert_pos'], 'unknown')

    def test_087_location(self):
        """ Test the location endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/location/rack_1/40000000/0028')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 3)
        self.assertIn('physical_location', response)
        self.assertIn('chassis_location', response)
        self.assertIn('request_received', response)

        physical_location = response['physical_location']
        self.assertIsInstance(physical_location, dict)
        self.assertEqual(len(physical_location), 3)
        self.assertIn('depth', physical_location)
        self.assertIn('horizontal', physical_location)
        self.assertIn('vertical', physical_location)
        self.assertEqual(physical_location['depth'], 'unknown')
        self.assertEqual(physical_location['horizontal'], 'unknown')
        self.assertEqual(physical_location['vertical'], 'unknown')

        chassis_location = response['chassis_location']
        self.assertIsInstance(chassis_location, dict)
        self.assertEqual(len(chassis_location), 4)
        self.assertIn('depth', chassis_location)
        self.assertIn('server_node', chassis_location)
        self.assertIn('horiz_pos', chassis_location)
        self.assertIn('vert_pos', chassis_location)
        self.assertEqual(chassis_location['depth'], 'unknown')
        self.assertEqual(chassis_location['server_node'], 'unknown')
        self.assertEqual(chassis_location['horiz_pos'], 'unknown')
        self.assertEqual(chassis_location['vert_pos'], 'unknown')

    def test_088_location(self):
        """ Test the location endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/location/rack_1/40000000/0027')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 3)
        self.assertIn('physical_location', response)
        self.assertIn('chassis_location', response)
        self.assertIn('request_received', response)

        physical_location = response['physical_location']
        self.assertIsInstance(physical_location, dict)
        self.assertEqual(len(physical_location), 3)
        self.assertIn('depth', physical_location)
        self.assertIn('horizontal', physical_location)
        self.assertIn('vertical', physical_location)
        self.assertEqual(physical_location['depth'], 'unknown')
        self.assertEqual(physical_location['horizontal'], 'unknown')
        self.assertEqual(physical_location['vertical'], 'unknown')

        chassis_location = response['chassis_location']
        self.assertIsInstance(chassis_location, dict)
        self.assertEqual(len(chassis_location), 4)
        self.assertIn('depth', chassis_location)
        self.assertIn('server_node', chassis_location)
        self.assertIn('horiz_pos', chassis_location)
        self.assertIn('vert_pos', chassis_location)
        self.assertEqual(chassis_location['depth'], 'unknown')
        self.assertEqual(chassis_location['server_node'], 'unknown')
        self.assertEqual(chassis_location['horiz_pos'], 'unknown')
        self.assertEqual(chassis_location['vert_pos'], 'unknown')

    def test_089_location(self):
        """ Test the location endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/location/rack_1/40000000/0022')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 3)
        self.assertIn('physical_location', response)
        self.assertIn('chassis_location', response)
        self.assertIn('request_received', response)

        physical_location = response['physical_location']
        self.assertIsInstance(physical_location, dict)
        self.assertEqual(len(physical_location), 3)
        self.assertIn('depth', physical_location)
        self.assertIn('horizontal', physical_location)
        self.assertIn('vertical', physical_location)
        self.assertEqual(physical_location['depth'], 'unknown')
        self.assertEqual(physical_location['horizontal'], 'unknown')
        self.assertEqual(physical_location['vertical'], 'unknown')

        chassis_location = response['chassis_location']
        self.assertIsInstance(chassis_location, dict)
        self.assertEqual(len(chassis_location), 4)
        self.assertIn('depth', chassis_location)
        self.assertIn('server_node', chassis_location)
        self.assertIn('horiz_pos', chassis_location)
        self.assertIn('vert_pos', chassis_location)
        self.assertEqual(chassis_location['depth'], 'unknown')
        self.assertEqual(chassis_location['server_node'], 'unknown')
        self.assertEqual(chassis_location['horiz_pos'], 'unknown')
        self.assertEqual(chassis_location['vert_pos'], 'unknown')

    def test_090_location(self):
        """ Test the location endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/location/rack_1/40000000/0011')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 3)
        self.assertIn('physical_location', response)
        self.assertIn('chassis_location', response)
        self.assertIn('request_received', response)

        physical_location = response['physical_location']
        self.assertIsInstance(physical_location, dict)
        self.assertEqual(len(physical_location), 3)
        self.assertIn('depth', physical_location)
        self.assertIn('horizontal', physical_location)
        self.assertIn('vertical', physical_location)
        self.assertEqual(physical_location['depth'], 'unknown')
        self.assertEqual(physical_location['horizontal'], 'unknown')
        self.assertEqual(physical_location['vertical'], 'unknown')

        chassis_location = response['chassis_location']
        self.assertIsInstance(chassis_location, dict)
        self.assertEqual(len(chassis_location), 4)
        self.assertIn('depth', chassis_location)
        self.assertIn('server_node', chassis_location)
        self.assertIn('horiz_pos', chassis_location)
        self.assertIn('vert_pos', chassis_location)
        self.assertEqual(chassis_location['depth'], 'unknown')
        self.assertEqual(chassis_location['server_node'], 'unknown')
        self.assertEqual(chassis_location['horiz_pos'], 'unknown')
        self.assertEqual(chassis_location['vert_pos'], 'unknown')

    def test_091_location(self):
        """ Test the location endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/location/rack_1/40000000/0012')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 3)
        self.assertIn('physical_location', response)
        self.assertIn('chassis_location', response)
        self.assertIn('request_received', response)

        physical_location = response['physical_location']
        self.assertIsInstance(physical_location, dict)
        self.assertEqual(len(physical_location), 3)
        self.assertIn('depth', physical_location)
        self.assertIn('horizontal', physical_location)
        self.assertIn('vertical', physical_location)
        self.assertEqual(physical_location['depth'], 'unknown')
        self.assertEqual(physical_location['horizontal'], 'unknown')
        self.assertEqual(physical_location['vertical'], 'unknown')

        chassis_location = response['chassis_location']
        self.assertIsInstance(chassis_location, dict)
        self.assertEqual(len(chassis_location), 4)
        self.assertIn('depth', chassis_location)
        self.assertIn('server_node', chassis_location)
        self.assertIn('horiz_pos', chassis_location)
        self.assertIn('vert_pos', chassis_location)
        self.assertEqual(chassis_location['depth'], 'unknown')
        self.assertEqual(chassis_location['server_node'], 'unknown')
        self.assertEqual(chassis_location['horiz_pos'], 'unknown')
        self.assertEqual(chassis_location['vert_pos'], 'unknown')

    def test_092_location(self):
        """ Test the location endpoint in IPMI mode.

        In this case, the given device does not exist.
        """
        r = http.get(PREFIX + '/location/rack_1/40000000/abcd')
        self.assertTrue(http.request_ok(r.status_code))

        # FIXME - in v1, location is not yet implemented so even though this device does
        # not exist, we will just get back location information for 'unknown'
        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 3)
        self.assertIn('physical_location', response)
        self.assertIn('chassis_location', response)
        self.assertIn('request_received', response)

    def test_093_led(self):
        """ Test the led endpoint in IPMI mode.
        """
        # fails because this is not a 'led' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/40000000/0100')

    def test_094_led(self):
        """ Test the led endpoint in IPMI mode.
        """
        # fails because this is not a 'led' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/40000000/0200')

    def test_095_led(self):
        """ Test the led endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/led/rack_1/40000000/0300')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        r = http.get(PREFIX + '/led/rack_1/40000000/0300/on')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        r = http.get(PREFIX + '/led/rack_1/40000000/0300/no_override')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        r = http.get(PREFIX + '/led/rack_1/40000000/0300/off')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        r = http.get(PREFIX + '/led/rack_1/40000000/0300')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

    def test_096_led(self):
        """ Test the led endpoint in IPMI mode.

        Test passing in an invalid LED command option.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/40000000/0300/non-option')

    def test_097_led(self):
        """ Test the led endpoint in IPMI mode.
        """
        # fails because this is not a 'led' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/40000000/0021')

    def test_098_led(self):
        """ Test the led endpoint in IPMI mode.
        """
        # fails because this is not a 'led' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/40000000/0042')

    def test_099_led(self):
        """ Test the led endpoint in IPMI mode.
        """
        # fails because this is not a 'led' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/40000000/0023')

    def test_100_led(self):
        """ Test the led endpoint in IPMI mode.
        """
        # fails because this is not a 'led' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/40000000/0024')

    def test_101_led(self):
        """ Test the led endpoint in IPMI mode.
        """
        # fails because this is not a 'led' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/40000000/0025')

    def test_102_led(self):
        """ Test the led endpoint in IPMI mode.
        """
        # fails because this is not a 'led' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/40000000/0026')

    def test_103_led(self):
        """ Test the led endpoint in IPMI mode.
        """
        # fails because this is not a 'led' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/40000000/0041')

    def test_104_led(self):
        """ Test the led endpoint in IPMI mode.
        """
        # fails because this is not a 'led' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/40000000/0028')

    def test_105_led(self):
        """ Test the led endpoint in IPMI mode.
        """
        # fails because this is not a 'led' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/40000000/0027')

    def test_106_led(self):
        """ Test the led endpoint in IPMI mode.
        """
        # fails because this is not a 'led' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/40000000/0022')

    def test_107_led(self):
        """ Test the led endpoint in IPMI mode.
        """
        # fails because this is not a 'led' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/40000000/0011')

    def test_108_led(self):
        """ Test the led endpoint in IPMI mode.
        """
        # fails because this is not a 'led' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/40000000/0012')

    def test_109_fan(self):
        """ Test the fan endpoint in IPMI mode.
        """
        # fails because this is not a 'fan' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/40000000/0100')

    def test_110_fan(self):
        """ Test the fan endpoint in IPMI mode.
        """
        # fails because this is not a 'fan' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/40000000/0200')

    def test_111_fan(self):
        """ Test the fan endpoint in IPMI mode.
        """
        # fails because this is not a 'fan' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/40000000/0300')

    def test_112_fan(self):
        """ Test the fan endpoint in IPMI mode.
        """
        # fails because this is not a 'fan' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/40000000/0021')

    def test_113_fan(self):
        """ Test the fan endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/fan/rack_1/40000000/0042')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('speed_rpm', response)
        self.assertEqual(response['speed_rpm'], 4100)

    def test_114_fan(self):
        """ Test the fan endpoint in IPMI mode.
        """
        # fails because this is not a 'fan' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/40000000/0023')

    def test_115_fan(self):
        """ Test the fan endpoint in IPMI mode.
        """
        # fails because this is not a 'fan' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/40000000/0024')

    def test_116_fan(self):
        """ Test the fan endpoint in IPMI mode.
        """
        # fails because this is not a 'fan' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/40000000/0025')

    def test_117_fan(self):
        """ Test the fan endpoint in IPMI mode.
        """
        # fails because this is not a 'fan' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/40000000/0026')

    def test_118_fan(self):
        """ Test the fan endpoint in IPMI mode.

        This should fail because the fan device is not present, so it
        cannot be read from.
        """
        r = http.get(PREFIX + '/fan/rack_1/40000000/0041')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('speed_rpm', response)
        self.assertIsInstance(response['speed_rpm'], float)

    def test_119_fan(self):
        """ Test the fan endpoint in IPMI mode.
        """
        # fails because this is not a 'fan' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/40000000/0028')

    def test_120_fan(self):
        """ Test the fan endpoint in IPMI mode.
        """
        # fails because this is not a 'fan' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/40000000/0027')

    def test_121_fan(self):
        """ Test the fan endpoint in IPMI mode.
        """
        # fails because this is not a 'fan' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/40000000/0022')

    def test_122_fan(self):
        """ Test the fan endpoint in IPMI mode.
        """
        # fails because this is not a 'fan' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/40000000/0011')

    def test_123_fan(self):
        """ Test the fan endpoint in IPMI mode.
        """
        # fails because this is not a 'fan' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/40000000/0012')

    def test_124_host_info(self):
        """ Test the host info endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/40000000/0100')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)

    def test_125_host_info(self):
        """ Test the host info endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/40000000/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)

    def test_126_host_info(self):
        """ Test the host info endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/40000000/0300')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)

    def test_127_host_info(self):
        """ Test the host info endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/40000000/0021')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)

    def test_128_host_info(self):
        """ Test the host info endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/40000000/0042')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)

    def test_129_host_info(self):
        """ Test the host info endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/40000000/0023')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)

    def test_130_host_info(self):
        """ Test the host info endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/40000000/0024')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)

    def test_131_host_info(self):
        """ Test the host info endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/40000000/0025')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)

    def test_132_host_info(self):
        """ Test the host info endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/40000000/0026')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)

    def test_133_host_info(self):
        """ Test the host info endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/40000000/0041')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)

    def test_134_host_info(self):
        """ Test the host info endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/40000000/0028')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)

    def test_135_host_info(self):
        """ Test the host info endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/40000000/0027')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)

    def test_136_host_info(self):
        """ Test the host info endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/40000000/0022')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)

    def test_137_host_info(self):
        """ Test the host info endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/40000000/0011')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)

    def test_138_host_info(self):
        """ Test the host info endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/40000000/0012')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)

    def test_139_host_info(self):
        """ Test the host info endpoint in IPMI mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/host_info/rack_1/40654321/0012')

    def test_140_host_info(self):
        """ Test the host info endpoint in IPMI mode.

        In this case, the given device id does not exist, but host info for
        IPMI does not check device id, so it should still return a valid response.
        """
        r = http.get(PREFIX + '/host_info/rack_1/40000000/abcd')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)

    def test_141_test_scan_by_host_and_ip(self):
        """ Test the Synse scan board endpoint using hostname and ip naming.
        """
        r = http.get(PREFIX + '/scan/rack_1/test-1')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('boards', response)

        boards = response['boards']
        self.assertIsInstance(boards, list)
        self.assertEqual(len(boards), 1)

        board = boards[0]
        self.assertIsInstance(board, dict)
        self.assertIn('board_id', board)
        self.assertEqual(board['board_id'], '40000000')
        self.assertIn('ip_addresses', board)
        self.assertEqual(board['ip_addresses'], ['192.168.1.100', '192.168.2.100', '192.168.1.100'])
        self.assertIn('hostnames', board)
        self.assertEqual(board['hostnames'], ['test-1', 'test-2', 'test-1'])
        self.assertIn('devices', board)

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

    def test_142_test_scan_by_host_and_ip(self):
        """ Test the Synse scan board endpoint using hostname and ip naming.
        """
        r = http.get(PREFIX + '/scan/rack_1/test-2')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('boards', response)

        boards = response['boards']
        self.assertIsInstance(boards, list)
        self.assertEqual(len(boards), 1)

        board = boards[0]
        self.assertIsInstance(board, dict)
        self.assertIn('board_id', board)
        self.assertEqual(board['board_id'], '40000000')
        self.assertIn('ip_addresses', board)
        self.assertEqual(board['ip_addresses'], ['192.168.1.100', '192.168.2.100', '192.168.1.100'])
        self.assertIn('hostnames', board)
        self.assertEqual(board['hostnames'], ['test-1', 'test-2', 'test-1'])
        self.assertIn('devices', board)

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

    def test_143_test_scan_by_host_and_ip(self):
        """ Test the Synse scan board endpoint using hostname and ip naming.
        """
        r = http.get(PREFIX + '/scan/rack_1/192.168.1.100')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('boards', response)

        boards = response['boards']
        self.assertIsInstance(boards, list)
        self.assertEqual(len(boards), 1)

        board = boards[0]
        self.assertIsInstance(board, dict)
        self.assertIn('board_id', board)
        self.assertEqual(board['board_id'], '40000000')
        self.assertIn('ip_addresses', board)
        self.assertEqual(board['ip_addresses'], ['192.168.1.100', '192.168.2.100', '192.168.1.100'])
        self.assertIn('hostnames', board)
        self.assertEqual(board['hostnames'], ['test-1', 'test-2', 'test-1'])
        self.assertIn('devices', board)

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

    def test_144_test_scan_by_host_and_ip(self):
        """ Test the Synse scan board endpoint using hostname and ip naming.
        """
        r = http.get(PREFIX + '/scan/rack_1/192.168.2.100')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('boards', response)

        boards = response['boards']
        self.assertIsInstance(boards, list)
        self.assertEqual(len(boards), 1)

        board = boards[0]
        self.assertIsInstance(board, dict)
        self.assertIn('board_id', board)
        self.assertEqual(board['board_id'], '40000000')
        self.assertIn('ip_addresses', board)
        self.assertEqual(board['ip_addresses'], ['192.168.1.100', '192.168.2.100', '192.168.1.100'])
        self.assertIn('hostnames', board)
        self.assertEqual(board['hostnames'], ['test-1', 'test-2', 'test-1'])
        self.assertIn('devices', board)

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

    def test_145_test_scan_by_bad_host(self):
        """ Test the host info endpoint in IPMI mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/scan/rack_1/test-3')

    def test_146_test_scan_by_bad_ip(self):
        """ Test the host info endpoint in IPMI mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/scan/rack_1/192.168.3.100')

    def test_147_read_by_host_and_ip(self):
        """ Test reading an IPMI device.
        """
        r = http.get(PREFIX + '/read/voltage/rack_1/test-1/0021')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('voltage', response)
        self.assertIsInstance(response['voltage'], float)

        r = http.get(PREFIX + '/read/voltage/rack_1/test-2/0021')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('voltage', response)
        self.assertIsInstance(response['voltage'], float)

        r = http.get(PREFIX + '/read/voltage/rack_1/192.168.1.100/0021')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('voltage', response)
        self.assertIsInstance(response['voltage'], float)

        r = http.get(PREFIX + '/read/voltage/rack_1/192.168.2.100/0021')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('voltage', response)
        self.assertIsInstance(response['voltage'], float)

    def test_148_test_read_by_bad_ip_host(self):
        """ Test the host info endpoint in IPMI mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/voltage/rack_1/192.168.3.100/0021')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/voltage/rack_1/test-3/0021')

    def test_149_power_by_ip_host(self):
        """ Test power control with IPMI.
        """
        r = http.get(PREFIX + '/power/rack_1/192.168.1.100/0100')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertTrue(150 <= response['input_power'] <= 250)

        r = http.get(PREFIX + '/power/rack_1/192.168.2.100/0100')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertTrue(150 <= response['input_power'] <= 250)

        r = http.get(PREFIX + '/power/rack_1/test-1/0100')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertTrue(150 <= response['input_power'] <= 250)

        r = http.get(PREFIX + '/power/rack_1/test-2/0100')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertTrue(150 <= response['input_power'] <= 250)

    def test_150_test_power_by_bad_ip_host(self):
        """ Test the host info endpoint in IPMI mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/power/rack_1/192.168.3.100/0100')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/power/rack_1/test-3/0100')

    def test_151_asset_by_host(self):
        """ Test the asset endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/asset/rack_1/test-1/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)

        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)

        self.assertIn('bmc_ip', response)
        bmc_ip = response['bmc_ip']
        self.assertEqual(bmc_ip, 'ipmi-emulator')  # name passed thru the cfg file which is the emulator container name

        self.assertIn('product_info', response)
        product_info = response['product_info']
        self.assertIsInstance(product_info, dict)
        for item in ['asset_tag', 'part_number', 'version', 'serial_number', 'product_name', 'manufacturer']:
            self.assertIn(item, product_info)

        self.assertIn('board_info', response)
        board_info = response['board_info']
        self.assertIsInstance(board_info, dict)
        for item in ['serial_number', 'part_number', 'product_name', 'manufacturer']:
            self.assertIn(item, board_info)

        self.assertIn('chassis_info', response)
        chassis_info = response['chassis_info']
        self.assertIsInstance(chassis_info, dict)
        for item in ['serial_number', 'part_number', 'chassis_type']:
            self.assertIn(item, chassis_info)

        r = http.get(PREFIX + '/asset/rack_1/test-2/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)

        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)

        self.assertIn('bmc_ip', response)
        bmc_ip = response['bmc_ip']
        self.assertEqual(bmc_ip, 'ipmi-emulator')  # name passed thru the cfg file which is the emulator container name

        self.assertIn('product_info', response)
        product_info = response['product_info']
        self.assertIsInstance(product_info, dict)
        for item in ['asset_tag', 'part_number', 'version', 'serial_number', 'product_name', 'manufacturer']:
            self.assertIn(item, product_info)

        self.assertIn('board_info', response)
        board_info = response['board_info']
        self.assertIsInstance(board_info, dict)
        for item in ['serial_number', 'part_number', 'product_name', 'manufacturer']:
            self.assertIn(item, board_info)

        self.assertIn('chassis_info', response)
        chassis_info = response['chassis_info']
        self.assertIsInstance(chassis_info, dict)
        for item in ['serial_number', 'part_number', 'chassis_type']:
            self.assertIn(item, chassis_info)

    def test_152_asset_by_ip(self):
        """ Test the asset endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/asset/rack_1/192.168.1.100/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)

        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)

        self.assertIn('bmc_ip', response)
        bmc_ip = response['bmc_ip']
        self.assertEqual(bmc_ip, 'ipmi-emulator')  # name passed thru the cfg file which is the emulator container name

        self.assertIn('product_info', response)
        product_info = response['product_info']
        self.assertIsInstance(product_info, dict)
        for item in ['asset_tag', 'part_number', 'version', 'serial_number', 'product_name', 'manufacturer']:
            self.assertIn(item, product_info)

        self.assertIn('board_info', response)
        board_info = response['board_info']
        self.assertIsInstance(board_info, dict)
        for item in ['serial_number', 'part_number', 'product_name', 'manufacturer']:
            self.assertIn(item, board_info)

        self.assertIn('chassis_info', response)
        chassis_info = response['chassis_info']
        self.assertIsInstance(chassis_info, dict)
        for item in ['serial_number', 'part_number', 'chassis_type']:
            self.assertIn(item, chassis_info)

        r = http.get(PREFIX + '/asset/rack_1/192.168.2.100/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)

        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)

        self.assertIn('bmc_ip', response)
        bmc_ip = response['bmc_ip']
        self.assertEqual(bmc_ip, 'ipmi-emulator')  # name passed thru the cfg file which is the emulator container name

        self.assertIn('product_info', response)
        product_info = response['product_info']
        self.assertIsInstance(product_info, dict)
        for item in ['asset_tag', 'part_number', 'version', 'serial_number', 'product_name', 'manufacturer']:
            self.assertIn(item, product_info)

        self.assertIn('board_info', response)
        board_info = response['board_info']
        self.assertIsInstance(board_info, dict)
        for item in ['serial_number', 'part_number', 'product_name', 'manufacturer']:
            self.assertIn(item, board_info)

        self.assertIn('chassis_info', response)
        chassis_info = response['chassis_info']
        self.assertIsInstance(chassis_info, dict)
        for item in ['serial_number', 'part_number', 'chassis_type']:
            self.assertIn(item, chassis_info)

    def test_153_test_asset_by_bad_ip_host(self):
        """ Test the host info endpoint in IPMI mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/192.168.3.100/0200')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/test-3/0200')

    def test_154_boot_target_by_host(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/boot_target/rack_1/test-1/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

        r = http.get(PREFIX + '/boot_target/rack_1/test-1/0200/pxe')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'pxe')

        r = http.get(PREFIX + '/boot_target/rack_1/test-1/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'pxe')

        r = http.get(PREFIX + '/boot_target/rack_1/test-1/0200/hdd')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/rack_1/test-1/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/rack_1/test-1/0200/no_override')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

        r = http.get(PREFIX + '/boot_target/rack_1/test-1/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

    def test_155_boot_target_by_host(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/boot_target/rack_1/test-2/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

        r = http.get(PREFIX + '/boot_target/rack_1/test-2/0200/pxe')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'pxe')

        r = http.get(PREFIX + '/boot_target/rack_1/test-2/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'pxe')

        r = http.get(PREFIX + '/boot_target/rack_1/test-2/0200/hdd')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/rack_1/test-2/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/rack_1/test-2/0200/no_override')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

        r = http.get(PREFIX + '/boot_target/rack_1/test-2/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

    def test_156_boot_target_by_ip(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/boot_target/rack_1/192.168.1.100/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.1.100/0200/pxe')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'pxe')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.1.100/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'pxe')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.1.100/0200/hdd')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.1.100/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.1.100/0200/no_override')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.1.100/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

    def test_157_boot_target_by_ip(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/boot_target/rack_1/192.168.2.100/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.2.100/0200/pxe')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'pxe')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.2.100/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'pxe')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.2.100/0200/hdd')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.2.100/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.2.100/0200/no_override')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.2.100/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

    def test_158_test_boot_target_by_bad_ip_host(self):
        """ Test the host info endpoint in IPMI mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/192.168.3.100/0200/no_override')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/test-3/0200/no_override')

    def test_159_location_by_host_ip(self):
        """ Test getting location information in IPMI mode.
        """
        r = http.get(PREFIX + '/location/rack_1/test-1')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 2)
        self.assertIn('physical_location', response)
        self.assertIn('request_received', response)

        physical_location = response['physical_location']
        self.assertIsInstance(physical_location, dict)
        self.assertEqual(len(physical_location), 3)
        self.assertIn('depth', physical_location)
        self.assertIn('horizontal', physical_location)
        self.assertIn('vertical', physical_location)
        self.assertEqual(physical_location['depth'], 'unknown')
        self.assertEqual(physical_location['horizontal'], 'unknown')
        self.assertEqual(physical_location['vertical'], 'unknown')

        r = http.get(PREFIX + '/location/rack_1/test-2')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 2)
        self.assertIn('physical_location', response)
        self.assertIn('request_received', response)

        physical_location = response['physical_location']
        self.assertIsInstance(physical_location, dict)
        self.assertEqual(len(physical_location), 3)
        self.assertIn('depth', physical_location)
        self.assertIn('horizontal', physical_location)
        self.assertIn('vertical', physical_location)
        self.assertEqual(physical_location['depth'], 'unknown')
        self.assertEqual(physical_location['horizontal'], 'unknown')
        self.assertEqual(physical_location['vertical'], 'unknown')

        r = http.get(PREFIX + '/location/rack_1/192.168.1.100')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 2)
        self.assertIn('physical_location', response)
        self.assertIn('request_received', response)

        physical_location = response['physical_location']
        self.assertIsInstance(physical_location, dict)
        self.assertEqual(len(physical_location), 3)
        self.assertIn('depth', physical_location)
        self.assertIn('horizontal', physical_location)
        self.assertIn('vertical', physical_location)
        self.assertEqual(physical_location['depth'], 'unknown')
        self.assertEqual(physical_location['horizontal'], 'unknown')
        self.assertEqual(physical_location['vertical'], 'unknown')

        r = http.get(PREFIX + '/location/rack_1/192.168.2.100')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 2)
        self.assertIn('physical_location', response)
        self.assertIn('request_received', response)

        physical_location = response['physical_location']
        self.assertIsInstance(physical_location, dict)
        self.assertEqual(len(physical_location), 3)
        self.assertIn('depth', physical_location)
        self.assertIn('horizontal', physical_location)
        self.assertIn('vertical', physical_location)
        self.assertEqual(physical_location['depth'], 'unknown')
        self.assertEqual(physical_location['horizontal'], 'unknown')
        self.assertEqual(physical_location['vertical'], 'unknown')

    def test_160_test_location_by_bad_ip_host(self):
        """ Test the host info endpoint in IPMI mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/location/rack_1/192.168.3.100/0200')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/location/rack_1/test-3/0200')

    def test_161_led_by_host(self):
        """ Test the led endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/led/rack_1/test-1/0300')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        r = http.get(PREFIX + '/led/rack_1/test-1/0300/on')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        r = http.get(PREFIX + '/led/rack_1/test-1/0300/no_override')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        r = http.get(PREFIX + '/led/rack_1/test-1/0300/off')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        r = http.get(PREFIX + '/led/rack_1/test-1/0300')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        r = http.get(PREFIX + '/led/rack_1/test-2/0300')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        r = http.get(PREFIX + '/led/rack_1/test-2/0300/on')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        r = http.get(PREFIX + '/led/rack_1/test-2/0300/no_override')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        r = http.get(PREFIX + '/led/rack_1/test-2/0300/off')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        r = http.get(PREFIX + '/led/rack_1/test-2/0300')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

    def test_162_led_by_ip(self):
        """ Test the led endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/led/rack_1/192.168.1.100/0300')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        r = http.get(PREFIX + '/led/rack_1/192.168.1.100/0300/on')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        r = http.get(PREFIX + '/led/rack_1/192.168.1.100/0300/no_override')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        r = http.get(PREFIX + '/led/rack_1/192.168.1.100/0300/off')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        r = http.get(PREFIX + '/led/rack_1/192.168.1.100/0300')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        r = http.get(PREFIX + '/led/rack_1/192.168.2.100/0300')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        r = http.get(PREFIX + '/led/rack_1/192.168.2.100/0300/on')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        r = http.get(PREFIX + '/led/rack_1/192.168.2.100/0300/no_override')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        r = http.get(PREFIX + '/led/rack_1/192.168.2.100/0300/off')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        r = http.get(PREFIX + '/led/rack_1/192.168.2.100/0300')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

    def test_163_test_led_by_bad_ip_host(self):
        """ Test the host info endpoint in IPMI mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/192.168.3.100/0300/off')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/test-3/0300/off')

    def test_164_fan_by_host_ip(self):
        """ Test the fan endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/fan/rack_1/test-1/0042')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('speed_rpm', response)
        self.assertEqual(response['speed_rpm'], 3915.0)

        r = http.get(PREFIX + '/fan/rack_1/test-2/0042')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('speed_rpm', response)
        self.assertEqual(response['speed_rpm'], 3730.0)

        r = http.get(PREFIX + '/fan/rack_1/192.168.1.100/0042')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('speed_rpm', response)
        self.assertEqual(response['speed_rpm'], 3730.0)

        r = http.get(PREFIX + '/fan/rack_1/192.168.2.100/0042')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('speed_rpm', response)
        self.assertEqual(response['speed_rpm'], 3545.0)

    def test_165_test_fan_by_bad_ip_host(self):
        """ Test the host info endpoint in IPMI mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/192.168.3.100/0042')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/test-3/0042')

    def test_166_host_info_by_host(self):
        """ Test the host info endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/test-1/0100')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)

        r = http.get(PREFIX + '/host_info/rack_1/test-2/0100')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)

    def test_167_host_info_by_ip(self):
        """ Test the host info endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/192.168.1.100/0100')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)

        r = http.get(PREFIX + '/host_info/rack_1/192.168.2.100/0100')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)

    def test_168_test_host_info_by_bad_ip_host(self):
        """ Test the host info endpoint in IPMI mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/host_info/rack_1/192.168.3.100/0100')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/host_info/rack_1/test-3/0100')

    def test_169_read_by_host_ip_and_name(self):
        """ Test reading an IPMI device.
        """
        # testing case-sensitivity as well - VCore or vcore should work here...
        r = http.get(PREFIX + '/read/voltage/rack_1/test-1/CPU vcore')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('voltage', response)
        self.assertIsInstance(response['voltage'], float)

        r = http.get(PREFIX + '/read/voltage/rack_1/test-2/CPU Vcore')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('voltage', response)
        self.assertIsInstance(response['voltage'], float)

        r = http.get(PREFIX + '/read/voltage/rack_1/192.168.1.100/CPU Vcore')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('voltage', response)
        self.assertIsInstance(response['voltage'], float)

        r = http.get(PREFIX + '/read/voltage/rack_1/192.168.2.100/CPU Vcore')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('voltage', response)
        self.assertIsInstance(response['voltage'], float)

    def test_170_test_read_by_bad_ip_host_device(self):
        """ Test the host info endpoint in IPMI mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/voltage/rack_1/192.168.3.100/CPU Vcore')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/voltage/rack_1/test-3/CPU Vcore')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/voltage/rack_1/test-1/CPU Wcore')

    def test_171_power_by_ip_host_device(self):
        """ Test power control with IPMI.
        """
        r = http.get(PREFIX + '/power/rack_1/192.168.1.100/power')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertTrue(150 <= response['input_power'] <= 250)

        r = http.get(PREFIX + '/power/rack_1/192.168.2.100/power')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertTrue(150 <= response['input_power'] <= 250)

        r = http.get(PREFIX + '/power/rack_1/test-1/power')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertTrue(150 <= response['input_power'] <= 250)

        r = http.get(PREFIX + '/power/rack_1/test-2/power')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertTrue(150 <= response['input_power'] <= 250)

    def test_172_test_power_by_bad_ip_host_device(self):
        """ Test the host info endpoint in IPMI mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/power/rack_1/192.168.3.100/0100')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/power/rack_1/test-3/0100')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/power/rack_1/test-1/pwoer')

    def test_173_asset_by_host_device(self):
        """ Test the asset endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/asset/rack_1/test-1/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)

        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)

        self.assertIn('bmc_ip', response)
        bmc_ip = response['bmc_ip']
        self.assertEqual(bmc_ip, 'ipmi-emulator')  # name passed thru the cfg file which is the emulator container name

        self.assertIn('product_info', response)
        product_info = response['product_info']
        self.assertIsInstance(product_info, dict)
        for item in ['asset_tag', 'part_number', 'version', 'serial_number', 'product_name', 'manufacturer']:
            self.assertIn(item, product_info)

        self.assertIn('board_info', response)
        board_info = response['board_info']
        self.assertIsInstance(board_info, dict)
        for item in ['serial_number', 'part_number', 'product_name', 'manufacturer']:
            self.assertIn(item, board_info)

        self.assertIn('chassis_info', response)
        chassis_info = response['chassis_info']
        self.assertIsInstance(chassis_info, dict)
        for item in ['serial_number', 'part_number', 'chassis_type']:
            self.assertIn(item, chassis_info)

        r = http.get(PREFIX + '/asset/rack_1/test-2/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)

        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)

        self.assertIn('bmc_ip', response)
        bmc_ip = response['bmc_ip']
        self.assertEqual(bmc_ip, 'ipmi-emulator')  # name passed thru the cfg file which is the emulator container name

        self.assertIn('product_info', response)
        product_info = response['product_info']
        self.assertIsInstance(product_info, dict)
        for item in ['asset_tag', 'part_number', 'version', 'serial_number', 'product_name', 'manufacturer']:
            self.assertIn(item, product_info)

        self.assertIn('board_info', response)
        board_info = response['board_info']
        self.assertIsInstance(board_info, dict)
        for item in ['serial_number', 'part_number', 'product_name', 'manufacturer']:
            self.assertIn(item, board_info)

        self.assertIn('chassis_info', response)
        chassis_info = response['chassis_info']
        self.assertIsInstance(chassis_info, dict)
        for item in ['serial_number', 'part_number', 'chassis_type']:
            self.assertIn(item, chassis_info)

    def test_174_asset_by_ip_device(self):
        """ Test the asset endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/asset/rack_1/192.168.1.100/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)

        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)

        self.assertIn('bmc_ip', response)
        bmc_ip = response['bmc_ip']
        self.assertEqual(bmc_ip, 'ipmi-emulator')  # name passed thru the cfg file which is the emulator container name

        self.assertIn('product_info', response)
        product_info = response['product_info']
        self.assertIsInstance(product_info, dict)
        for item in ['asset_tag', 'part_number', 'version', 'serial_number', 'product_name', 'manufacturer']:
            self.assertIn(item, product_info)

        self.assertIn('board_info', response)
        board_info = response['board_info']
        self.assertIsInstance(board_info, dict)
        for item in ['serial_number', 'part_number', 'product_name', 'manufacturer']:
            self.assertIn(item, board_info)

        self.assertIn('chassis_info', response)
        chassis_info = response['chassis_info']
        self.assertIsInstance(chassis_info, dict)
        for item in ['serial_number', 'part_number', 'chassis_type']:
            self.assertIn(item, chassis_info)

        r = http.get(PREFIX + '/asset/rack_1/192.168.2.100/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 6)

        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)

        self.assertIn('bmc_ip', response)
        bmc_ip = response['bmc_ip']
        self.assertEqual(bmc_ip, 'ipmi-emulator')  # name passed thru the cfg file which is the emulator container name

        self.assertIn('product_info', response)
        product_info = response['product_info']
        self.assertIsInstance(product_info, dict)
        for item in ['asset_tag', 'part_number', 'version', 'serial_number', 'product_name', 'manufacturer']:
            self.assertIn(item, product_info)

        self.assertIn('board_info', response)
        board_info = response['board_info']
        self.assertIsInstance(board_info, dict)
        for item in ['serial_number', 'part_number', 'product_name', 'manufacturer']:
            self.assertIn(item, board_info)

        self.assertIn('chassis_info', response)
        chassis_info = response['chassis_info']
        self.assertIsInstance(chassis_info, dict)
        for item in ['serial_number', 'part_number', 'chassis_type']:
            self.assertIn(item, chassis_info)

    def test_175_test_asset_by_bad_ip_host_device(self):
        """ Test the host info endpoint in IPMI mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/192.168.3.100/0200')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/test-3/0200')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/test-3/ssytem')

    def test_176_boot_target_by_host_device(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/boot_target/rack_1/test-1/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

        r = http.get(PREFIX + '/boot_target/rack_1/test-1/system/pxe')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'pxe')

        r = http.get(PREFIX + '/boot_target/rack_1/test-1/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'pxe')

        r = http.get(PREFIX + '/boot_target/rack_1/test-1/system/hdd')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/rack_1/test-1/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/rack_1/test-1/system/no_override')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

        r = http.get(PREFIX + '/boot_target/rack_1/test-1/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

    def test_177_boot_target_by_host_device(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/boot_target/rack_1/test-2/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

        r = http.get(PREFIX + '/boot_target/rack_1/test-2/system/pxe')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'pxe')

        r = http.get(PREFIX + '/boot_target/rack_1/test-2/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'pxe')

        r = http.get(PREFIX + '/boot_target/rack_1/test-2/system/hdd')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/rack_1/test-2/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/rack_1/test-2/system/no_override')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

        r = http.get(PREFIX + '/boot_target/rack_1/test-2/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

    def test_178_boot_target_by_ip_device(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/boot_target/rack_1/192.168.1.100/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.1.100/system/pxe')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'pxe')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.1.100/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'pxe')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.1.100/system/hdd')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.1.100/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.1.100/system/no_override')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.1.100/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

    def test_179_boot_target_by_ip_device(self):
        """ Test the boot target endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/boot_target/rack_1/192.168.2.100/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.2.100/system/pxe')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'pxe')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.2.100/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'pxe')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.2.100/system/hdd')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.2.100/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'hdd')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.2.100/system/no_override')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

        r = http.get(PREFIX + '/boot_target/rack_1/192.168.2.100/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('target', response)
        self.assertEqual(response['target'], 'no_override')

    def test_180_test_boot_target_by_bad_ip_host_device(self):
        """ Test the host info endpoint in IPMI mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/192.168.3.100/0200/no_override')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/test-3/0200/no_override')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/boot_target/rack_1/test-1/ssytem/no_override')

    def test_181_led_by_host_device(self):
        """ Test the led endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/led/rack_1/test-1/led')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        r = http.get(PREFIX + '/led/rack_1/test-1/led/on')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        r = http.get(PREFIX + '/led/rack_1/test-1/led/no_override')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        r = http.get(PREFIX + '/led/rack_1/test-1/led/off')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        r = http.get(PREFIX + '/led/rack_1/test-1/led')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        r = http.get(PREFIX + '/led/rack_1/test-2/led')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        r = http.get(PREFIX + '/led/rack_1/test-2/led/on')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        r = http.get(PREFIX + '/led/rack_1/test-2/led/no_override')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        r = http.get(PREFIX + '/led/rack_1/test-2/led/off')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        r = http.get(PREFIX + '/led/rack_1/test-2/led')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

    def test_182_led_by_ip_device(self):
        """ Test the led endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/led/rack_1/192.168.1.100/led')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        r = http.get(PREFIX + '/led/rack_1/192.168.1.100/led/on')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        r = http.get(PREFIX + '/led/rack_1/192.168.1.100/led/no_override')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        r = http.get(PREFIX + '/led/rack_1/192.168.1.100/led/off')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        r = http.get(PREFIX + '/led/rack_1/192.168.1.100/led')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        r = http.get(PREFIX + '/led/rack_1/192.168.2.100/LED')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        r = http.get(PREFIX + '/led/rack_1/192.168.2.100/led/on')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        r = http.get(PREFIX + '/led/rack_1/192.168.2.100/led/no_override')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'on')

        r = http.get(PREFIX + '/led/rack_1/192.168.2.100/led/off')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

        r = http.get(PREFIX + '/led/rack_1/192.168.2.100/led')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertEqual(response['led_state'], 'off')

    def test_183_test_led_by_bad_ip_host_device(self):
        """ Test the host info endpoint in IPMI mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/192.168.3.100/0300/off')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/test-3/0300/off')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/test-1/ledd/off')

    def test_184_fan_by_host_ip_device(self):
        """ Test the fan endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/fan/rack_1/test-1/0042')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('speed_rpm', response)
        self.assertEqual(response['speed_rpm'], 3915.0)

        r = http.get(PREFIX + '/fan/rack_1/test-2/sys fan')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('speed_rpm', response)
        self.assertEqual(response['speed_rpm'], 4100.0)

        r = http.get(PREFIX + '/fan/rack_1/192.168.1.100/sys fan')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('speed_rpm', response)
        self.assertEqual(response['speed_rpm'], 3915.0)

        r = http.get(PREFIX + '/fan/rack_1/192.168.2.100/sys fan')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('speed_rpm', response)
        self.assertEqual(response['speed_rpm'], 3730.0)

    def test_185_test_fan_by_bad_ip_host_device(self):
        """ Test the host info endpoint in IPMI mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/192.168.3.100/0042')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/test-3/0042')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/test-1/sys_fan')

    def test_186_host_info_by_host_device(self):
        """ Test the host info endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/test-1/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)

        r = http.get(PREFIX + '/host_info/rack_1/test-2/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)

    def test_187_host_info_by_ip_device(self):
        """ Test the host info endpoint in IPMI mode.
        """
        r = http.get(PREFIX + '/host_info/rack_1/192.168.1.100/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)

        r = http.get(PREFIX + '/host_info/rack_1/192.168.2.100/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)

        self.assertIn('ip_addresses', response)
        ip_addresses = response['ip_addresses']
        self.assertIsInstance(ip_addresses, list)
        self.assertEqual(len(ip_addresses), 3)
        self.assertEqual(ip_addresses[2], '192.168.1.100')

        self.assertIn('hostnames', response)
        hostnames = response['hostnames']
        self.assertIsInstance(hostnames, list)
        self.assertEqual(len(hostnames), 3)
