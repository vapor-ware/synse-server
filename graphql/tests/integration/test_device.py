""" Tests for the device schema

    Author: Thomas Rampelberg
    Date:   2/27/2017

    \\//
     \/apor IO
"""

from nose.plugins.attrib import attr  # noqa

from ..util import BaseSchemaTest


class TestDevice(BaseSchemaTest):

    def get_devices(self, query):
        return self.run_query(query).data.get("racks")[0].get("boards")[0].get(
            "devices")

    def check_keys(self, data, keys):
        self.assertItemsEqual(data.keys(), keys.keys())
        for k, v in keys.items():
            if len(v.keys()) > 0:
                self.check_keys(data.get(k), keys.get(k))

    def test_basic_query(self):
        keys = {
            "id": {},
            "device_type": {},
            "location": {
                "chassis_location": {
                    "depth": {},
                    "vert_pos": {},
                    "horiz_pos": {},
                    "server_node": {}
                },
                "physical_location": {
                    "depth": {},
                    "horizontal": {},
                    "vertical": {}
                }
            }
        }

        self.check_keys(self.get_devices("test_devices")[0], keys)

    def test_system_device(self):
        keys = {
            "device_type": {},
            "ip_addresses": {},
            "hostnames": {},
            "asset": {
                "board_info": {
                  "manufacturer": {},
                  "part_number": {},
                  "product_name": {},
                  "serial_number": {}
                },
                "chassis_info": {
                  "chassis_type": {},
                  "part_number": {},
                  "serial_number": {}
                },
                "product_info": {
                  "asset_tag": {},
                  "manufacturer": {},
                  "part_number": {},
                  "product_name": {},
                  "serial_number": {},
                  "version": {}
                }
            }
        }
        self.check_keys(self.get_devices("test_systemdevice")[0], keys)

    def test_type_arg(self):
        self.assertEqual(len(self.get_devices("test_device_type_arg")), 1)

    def test_temperature(self):
        keys = [
            "temperature_c"
        ]
        self.assertItemsEqual(
            self.get_devices("test_temp_device")[0].keys(), keys)

    def test_power(self):
        keys = [
            "input_power",
            "over_current",
            "power_ok",
            "power_status"
        ]
        self.assertItemsEqual(
            self.get_devices("test_power_device")[0].keys(), keys)

    def test_led(self):
        keys = [
            "led_state"
        ]
        self.assertItemsEqual(
            self.get_devices("test_led_device")[0].keys(), keys)

    def test_fan_speed(self):
        keys = [
            "health",
            "states",
            "speed_rpm"
        ]
        self.assertItemsEqual(
            self.get_devices("test_fan_speed_device")[0].keys(), keys)
