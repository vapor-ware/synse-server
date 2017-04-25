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
        return self.run_query(query).data["clusters"][0]["racks"][0][
            "boards"][0]["devices"]

    def test_basic_query(self):
        keys = [
            "id",
            "device_type",
            "location"
        ]
        chassis_keys = [
            "depth",
            "vert_pos",
            "horiz_pos",
            "server_node"
        ]
        physical_keys = [
            "depth",
            "horizontal",
            "vertical"
        ]
        device = self.get_devices("test_devices")[0]
        self.assertItemsEqual(device.keys(), keys)
        self.assertItemsEqual(
            device.get("location").get("chassis_location").keys(),
            chassis_keys)
        self.assertItemsEqual(
            device.get("location").get("physical_location").keys(),
            physical_keys)

    def test_system_device(self):
        keys = [
            "device_type",
            "ip_addresses",
            "hostnames",
            "asset"
        ]
        self.assertItemsEqual(
            self.get_devices("test_systemdevice")[0].keys(), keys)

    def test_type_arg(self):
        self.assertEqual(len(self.get_devices("test_device_type_arg")), 1)

    def test_pressure(self):
        keys = [
            "pressure_kpa"
        ]
        self.assertItemsEqual(
            self.get_devices("test_pressure_device")[0].keys(), keys)

    def test_temperature(self):
        keys = [
            "temperature_c"
        ]
        self.assertItemsEqual(
            self.get_devices("test_temp_device")[0].keys(), keys)

    def test_vapor_rectifier(self):
        keys = [
            "input_power",
            "input_voltage",
            "output_current",
            "over_current",
            "pmbus_raw",
            "power_ok",
            "power_status",
            "under_voltage"
        ]
        self.assertItemsEqual(
            self.get_devices("test_vapor_rectifier_device")[0].keys(), keys)

    def test_power(self):
        keys = [
            "input_power",
            "input_voltage",
            "output_current",
            "over_current",
            "pmbus_raw",
            "power_ok",
            "power_status",
            "under_voltage"
        ]
        self.assertItemsEqual(
            self.get_devices("test_power_device")[0].keys(), keys)

    def test_vapor_led(self):
        keys = [
            "blink_state",
            "led_color",
            "led_state"
        ]
        self.assertItemsEqual(
            self.get_devices("test_vapor_led_device")[0].keys(), keys)

    def test_led(self):
        keys = [
            "led_state"
        ]
        self.assertItemsEqual(
            self.get_devices("test_led_device")[0].keys(), keys)

    def test_fan_speed(self):
        keys = [
            "fan_mode",
            "speed_rpm"
        ]
        self.assertItemsEqual(
            self.get_devices("test_fan_speed_device")[0].keys(), keys)

    def test_vapor_fan(self):
        keys = [
            "fan_mode",
            "speed_rpm"
        ]
        self.assertItemsEqual(
            self.get_devices("test_vapor_fan_device")[0].keys(), keys)
