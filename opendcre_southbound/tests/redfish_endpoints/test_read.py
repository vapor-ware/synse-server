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

class RedfishReadTestCase(unittest.TestCase):
    """ Test reading devices with the Redfish emulator running
    """
    def test_01_read(self):
        """ Test reading a Redfish device - voltage.
        """
        r = http.get(PREFIX + '/read/voltage/rack_1/70000000/0005')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('voltage', response)
        self.assertIsInstance(response['voltage'], float)

    def test_02_read(self):
        """ Test reading a Redfish device - fan_speed.
        """
        r = http.get(PREFIX + '/read/fan_speed/rack_1/70000000/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('speed_rpm', response)
        self.assertIsInstance(response['speed_rpm'], float)
        self.assertEqual(response['speed_rpm'], 2050.0)

    def test_03_read(self):
        """ Test reading a Redfish device - temperature.
        """
        r = http.get(PREFIX + '/read/temperature/rack_1/70000000/0004')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)

    def test_04_read(self):
        """ Test reading a Redfish device - power_supply.
        """
        r = http.get(PREFIX + '/read/power_supply/rack_1/70000000/0007')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)

    def test_05_read(self):
        """ Test reading a Redfish device.

        This should fail since the fan device is not 'present' in the emulator.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/fan_speed/rack_1/70000000/0041')

    def test_06_read(self):
        """ Test reading a Redfish device.

        This should fail since 'power' is unsupported for Redfish reads.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/rack_1/power/70000000/0100')

    def test_07_read(self):
        """ Test reading a Redfish device.

        This should fail since 'system' is unsupported for Redfish reads.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/rack_1/system/70000000/0200')

    def test_08_read(self):
        """ Test reading a Redfish device.

        This should fail since 'led' is unsupported for Redfish reads.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/rack_1/led/70000000/0300')

    def test_09_read(self):
        """ Test reading a Redfish device.
        """
        r = http.get(PREFIX + '/read/voltage/rack_1/redfish-emulator/0005')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('voltage', response)
        self.assertIsInstance(response['voltage'], float)

        r = http.get(PREFIX + '/read/voltage/rack_1/redfish-emulator/VRM1 Voltage')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('states', response)
        self.assertIn('health', response)
        self.assertIn('voltage', response)
        self.assertIsInstance(response['voltage'], float)

    def test_10_read(self):
        """ Test reading a Redfish device.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/voltage/rack_1/192.168.3.100/0005')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/voltage/rack_1/test-3/0005')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/voltage/rack_1/192.168.3.100/VRM1 Voltage')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/voltage/rack_1/redfish-emulator/VRM0 Woltige')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/voltage/rack_1/test-1/VRM1 Voltage')

    def test_11_read(self):
        """ Test reading a Redfish device.

        This will turn the power off to test reads when the BMC in unpowered.
        In these cases, we expect that the reads should not return data.
        """
        # turn the power off
        r = http.get(PREFIX + '/power/rack_1/70000000/0100/off')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 4)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertEqual(response['power_status'], 'off')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        #TODO - self.assertEqual(response['input_power'], 0) when emulator changes this value

        # TODO - check the read values for devices that have already been tested above when emulator
        # TODO (con't) - changes these values
        # with self.assertRaises(VaporHTTPError):
        #     http.get(PREFIX + '/read/voltage/rack_1/70000000/0005')

        # with self.assertRaises(VaporHTTPError):
        #     http.get(PREFIX + '/read/voltage/rack_1/70000000/0001')

        # with self.assertRaises(VaporHTTPError):
        #     http.get(PREFIX + '/read/voltage/rack_1/70000000/0004')

        # with self.assertRaises(VaporHTTPError):
        #     http.get(PREFIX + '/read/voltage/rack_1/70000000/0007')

        # turn the power back on
        r = http.get(PREFIX + '/power/rack_1/70000000/0100/on')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(len(response), 4)
        self.assertIn('power_status', response)
        self.assertIn('power_ok', response)
        self.assertIn('over_current', response)
        self.assertIn('input_power', response)
        self.assertEqual(response['power_status'], 'on')
        self.assertEqual(response['power_ok'], True)
        self.assertEqual(response['over_current'], False)
        self.assertEqual(response['input_power'], 344.0)