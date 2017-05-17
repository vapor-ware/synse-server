""" Tests for the device schema

    Author: Thomas Rampelberg
    Date:   2/27/2017

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

from nose.plugins.attrib import attr  # noqa

from ..util import BaseSchemaTest


class TestDevice(BaseSchemaTest):

    def get_devices(self, query):
        return self.run_query(query).data.get('racks')[0].get('boards')[0].get(
            'devices')

    def get_all_devices(self, query):
        """ Gets all devices from a query.

        Additionally, this filters out empty responses. This is needed for
        I2C device queries in particular, e.g. we could get a response from
        a pressure query looking like:
            {
              "racks": [
                {
                  "boards": [
                    {
                      "devices": []
                    },
                    {
                      "devices": [
                        {
                          "pressure_kpa": -6.0,
                          "timestamp": 1495036581,
                          "request_received": 1495036581
                        }
                      ]
                    },
                    {
                      "devices": []
                    }
                  ]
                }
              ]
            }

        If the device list is empty, it will be omitted.
        """
        res = self.run_query(query).data
        for rack in res.get('racks'):
            for board in rack['boards']:
                for device in board['devices']:
                    if device:
                        yield device

    def check_keys(self, data, keys):
        self.assertItemsEqual(data.keys(), keys.keys())
        for k, v in keys.items():
            if len(v.keys()) > 0:
                self.check_keys(data.get(k), keys.get(k))

    def test_basic_query(self):
        keys = {
            'id': {},
            'device_type': {},
            'timestamp': {},
            'request_received': {},
            'location': {
                'chassis_location': {
                    'depth': {},
                    'vert_pos': {},
                    'horiz_pos': {},
                    'server_node': {}
                },
                'physical_location': {
                    'depth': {},
                    'horizontal': {},
                    'vertical': {}
                }
            }
        }

        self.check_keys(self.get_devices('test_devices')[0], keys)

    def test_system_device(self):
        keys = {
            'device_type': {},
            'ip_addresses': {},
            'hostnames': {},
            'timestamp': {},
            'request_received': {},
            'asset': {
                'board_info': {
                  'manufacturer': {},
                  'part_number': {},
                  'product_name': {},
                  'serial_number': {}
                },
                'chassis_info': {
                  'chassis_type': {},
                  'part_number': {},
                  'serial_number': {}
                },
                'product_info': {
                  'asset_tag': {},
                  'manufacturer': {},
                  'part_number': {},
                  'product_name': {},
                  'serial_number': {},
                  'version': {}
                }
            }
        }
        self.check_keys(self.get_devices('test_systemdevice')[0], keys)

    def test_type_arg(self):
        self.assertEqual(len(self.get_devices('test_device_type_arg')), 1)

    def test_temperature(self):
        keys = [
            'temperature_c',
            'timestamp',
            'request_received'
        ]
        self.assertItemsEqual(
            self.get_devices('test_temp_device')[0].keys(), keys)

    def test_power(self):
        keys = [
            'input_power',
            'over_current',
            'power_ok',
            'power_status',
            'timestamp',
            'request_received'
        ]
        self.assertItemsEqual(
            self.get_devices('test_power_device')[0].keys(), keys)

    def test_led(self):
        keys = [
            'led_state',
            'timestamp',
            'request_received'
        ]
        self.assertItemsEqual(
            self.get_devices('test_led_device')[0].keys(), keys)

    def test_fan_speed(self):
        keys = [
            'health',
            'states',
            'speed_rpm',
            'timestamp',
            'request_received'
        ]
        self.assertItemsEqual(
            self.get_devices('test_fan_speed_device')[0].keys(), keys)

    def test_voltage(self):
        keys = [
            'voltage',
            'timestamp',
            'request_received'
        ]
        self.assertItemsEqual(
            self.get_devices('test_voltage_device')[0].keys(), keys)

    def test_pressure(self):
        keys = [
            'pressure_kpa',
            'timestamp',
            'request_received'
        ]
        for device in self.get_all_devices('test_pressure_device'):
            self.assertItemsEqual(device.keys(), keys)
