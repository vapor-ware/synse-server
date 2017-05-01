#!/usr/bin/env python
""" OpenDCRE Southbound Redfish Endpoint Tests

    Author: Morgan Morley Mills, based off IPMI tests by Erick Daniszewski
    Date:   02/06/2017

    \\//
     \/apor IO
"""

import unittest

from opendcre_southbound.tests.test_config import PREFIX
from vapor_common import http
from vapor_common.errors import VaporHTTPError

class RedfishAssetTestCase(unittest.TestCase):
    """ Test asset reads with the Redfish emulator running
    """
    def test_01_asset(self):
        """ Test the asset endpoint in Redfish mode.
        """
        r = http.get(PREFIX + '/asset/rack_1/70000000/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 4)

        self.assertIn('redfish_ip', response)
        redfish_ip = response['redfish_ip']
        self.assertEqual(redfish_ip, 'redfish-emulator')  # name passed thru the cfg file which is the emulator container name

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

    def test_02_asset(self):
        """ Test the asset endpoint in Redfish mode.
        """
        # fails because this is not a 'system' device.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/70000000/0100')

    def test_03_asset(self):
        """ Test the asset endpoint in Redfish mode.
        """
        # fails because this is not a 'system' device - led.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/70000000/0300')

    def test_04_asset(self):
        """ Test the asset endpoint in Redfish mode.
        """
        # fails because this is not a 'system' device - fan_speed.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/70000000/0001')

    def test_05_asset(self):
        """ Test the asset endpoint in Redfish mode.
        """
        # fails because this is not a 'system' device - temperature.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/70000000/0002')

    def test_06_asset(self):
        """ Test the asset endpoint in Redfish mode.
        """
        # fails because this is not a 'system' device - voltage.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/70000000/0006')

    def test_07_asset(self):
        """ Test the asset endpoint in Redfish mode.
        """
        # fails because this is not a 'system' device - power_supply.
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/70000000/0007')

    def test_08_asset(self):
        """ Test the asset endpoint in Redfish mode.

        Tests getting asset info of a device that does not exist
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/70000000/0056')

    def test_09_asset(self):
        """ Test the asset endpoint in Redfish mode.
        """
        r = http.get(PREFIX + '/asset/rack_1/redfish-emulator/0200')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 4)

        self.assertIn('redfish_ip', response)
        redfish_ip = response['redfish_ip']
        self.assertEqual(redfish_ip, 'redfish-emulator')  # name passed thru the cfg file which is the emulator container name

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

    def test_10_asset(self):
        """ Test the asset endpoint in Redfish mode.
        """
        r = http.get(PREFIX + '/asset/rack_1/redfish-emulator/system')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 4)

        self.assertIn('redfish_ip', response)
        redfish_ip = response['redfish_ip']
        self.assertEqual(redfish_ip, 'redfish-emulator')  # name passed thru the cfg file which is the emulator container name

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

    def test_11_asset(self):
        """ Test the host info endpoint in Redfish mode.

        In this case, the given board id does not exist.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/192.168.3.100/0200')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/test-3/0200')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/asset/rack_1/redfish-emulator/ssytem')