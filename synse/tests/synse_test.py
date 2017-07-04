#!/usr/bin/env python
""" Synse SNMP Device Registration Tests

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
import logging
import unittest

from vapor_common.errors import VaporHTTPError
from vapor_common.tests.utils.strings import _S

logger = logging.getLogger(__name__)


class SynseHttpTest(unittest.TestCase):
    """Wrapper class around unittest.TestCase containing common methods for
    testing nd verification."""

    def _get_rack_by_id(self, response, rack_id):
        """Get a rack from the scan response given the rack id.
        :param response: The http response from Synse.
        :param rack_id: The string id of the rack in the scan response."""
        racks = response[_S.RACKS]
        self.assertIsInstance(racks, list)
        list_of_one_rack = [r for r in racks if r[_S.RACK_ID] == rack_id]
        rack = list_of_one_rack[0]
        return rack

    def _verify_common_board_fields(self, board):
        """Helper to make sure the fields are there and the data type is
        correct. No verification as to what is in them.
        :param board: The string id of the board in the scan response."""
        self.assertIn(_S.DEVICES, board)
        self.assertIsInstance(board[_S.DEVICES], list)

        devices = board[_S.DEVICES]
        device0 = devices[0]
        self.assertIsInstance(device0, dict)

        self.assertEquals(3, len(device0))
        self.assertIn(_S.DEVICE_ID, device0)
        self.assertIn(_S.DEVICE_INFO, device0)
        self.assertIn(_S.DEVICE_TYPE, device0)

    def _verify_common_rack_fields(self, rack):
        """Helper to make sure the fields are there and the data type is
        correct. No verification as to what is in them.
        :param rack: The rack to verify."""

        # Verify rack_id.
        self.assertIn(_S.RACK_ID, rack)

        # Verify hostnames.
        self.assertIn(_S.HOSTNAMES, rack)
        self.assertIsInstance(rack[_S.HOSTNAMES], list)

        # Verify ip_addresses.
        self.assertIn(_S.IP_ADDRESSES, rack)
        self.assertIsInstance(rack[_S.IP_ADDRESSES], list)

        # Verify boards.
        self.assertIn(_S.BOARDS, rack)
        self.assertIsInstance(rack[_S.BOARDS], list)

    def _verify_device(self, device, expected_device_id, expected_device_info, expected_device_type):
        """Verify device field in the scan results.
        :param device: A single device in the scan results. Example:
        {
            "device_id": "0010",
            "device_info": "power",
            "device_type": "power"
        }
        :param expected_device_id: The expected device id in the device.
        :param expected_device_info: The expected device info in the device.
        :param expected_device_type: The expected device type in the device."""
        self.assertEquals(3, len(device))
        self.assertEquals(expected_device_id, device[_S.DEVICE_ID])
        self.assertEquals(expected_device_info, device[_S.DEVICE_INFO])
        self.assertEquals(expected_device_type, device[_S.DEVICE_TYPE])

    def _verify_expected_rack_count(self, response, expected_rack_count):
        """Verify the expected rack count for a scan.
        :param response: The scan results.
        :param expected_rack_count: The number of racks we expect in response."""
        self.assertIsInstance(response, dict)
        self.assertIn(_S.RACKS, response)

        # Verify expected rack count.
        racks = response[_S.RACKS]
        self.assertIsInstance(racks, list)
        self.assertEqual(expected_rack_count, len(racks))

    def _verify_led_response(self, response, led_state, led_color, blink_state):
        """Verify the LED response is what we expect.
        :param response: The raw LED response from Synse.
        :param led_state: The expected led_state reading in the response.
        :param led_color: The expected led_color reading in the response.
        :param blink_state: The expected blink_state reading in the response.
        :raises On failure."""
        self.assertIsInstance(response, dict)
        self.assertEquals(5, len(response))
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertIn(_S.LED_STATE, response)
        self.assertEquals(led_state, response[_S.LED_STATE])
        self.assertIn(_S.LED_COLOR, response)
        self.assertEquals(led_color, response[_S.LED_COLOR])
        self.assertIn(_S.BLINK_STATE, response)
        self.assertEquals(blink_state, response[_S.BLINK_STATE])

    def _verify_power_response(
            self, response, input_power, over_current, power_ok, power_status):
        """Verify the power response is what we expect.
        :param response: The raw power response from Synse.
        :param input_power: The expected input_power reading in the response.
        :param over_current: The expected over_current reading in the response.
        :param power_ok: The expected power_ok reading in the response.
        :param power_status: The expected power_status reading in the response.
        :raises On failure."""
        self.assertIsInstance(response, dict)
        self.assertEquals(6, len(response))
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertIn(_S.INPUT_POWER, response)
        self.assertEquals(input_power, response[_S.INPUT_POWER])
        self.assertIn(_S.OVER_CURRENT, response)
        self.assertEquals(over_current, response[_S.OVER_CURRENT])
        self.assertIn(_S.POWER_OK, response)
        self.assertEquals(power_ok, response[_S.POWER_OK])
        self.assertIn(_S.POWER_STATUS, response)
        self.assertEquals(power_status, response[_S.POWER_STATUS])

    def _verify_read_fan_response(self, response, health, states, speed_rpm):
        """Verify the voltate read response is what we expect.
        :param response: The raw read response from Synse.
        :param health: The expected health reading in the response.
        :param states: The expected states reading in the response.
        :param speed_rpm: The expected speed_rpm reading in the response.
        :raises On failure."""
        self.assertIsInstance(response, dict)
        self.assertEquals(5, len(response))
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertIn(_S.HEALTH, response)
        self.assertEquals(health, response[_S.HEALTH])
        self.assertIn(_S.STATES, response)
        self.assertIsInstance(response[_S.STATES], list)
        self.assertEquals(states, response[_S.STATES])
        self.assertIn(_S.SPEED_RPM, response)
        self.assertEquals(speed_rpm, response[_S.SPEED_RPM])

    def _verify_read_temperature_response(self, response, health, states, temperature_c):
        """
        Verify the read response is what we expect for a temperature reading.
        :param response: The raw read response from Synse.
        :param health: The expected health reading in the response.
        :param states: The expected states reading in the response.
        :param temperature_c: The expected temperature_c reading in the response.
        :raises On failure."""
        self.assertIsInstance(response, dict)
        self.assertEquals(5, len(response))
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertIn(_S.HEALTH, response)
        self.assertEquals(health, response[_S.HEALTH])
        self.assertIn(_S.STATES, response)
        self.assertIsInstance(response[_S.STATES], list)
        self.assertEquals(states, response[_S.STATES])
        self.assertIn(_S.TEMPERATURE_C, response)
        self.assertEquals(temperature_c, response[_S.TEMPERATURE_C])

    def _verify_read_voltage_response(self, response, health, states, voltage):
        """Verify the voltate read response is what we expect.
        :param response: The raw read response from Synse.
        :param health: The expected health reading in the response.
        :param states: The expected states reading in the response.
        :param voltage: The expected voltage reading in the response.
        :raises On failure."""
        self.assertIsInstance(response, dict)
        self.assertEquals(5, len(response))
        self.assertIn('request_received', response)
        self.assertIn('timestamp', response)
        self.assertIn(_S.HEALTH, response)
        self.assertEquals(health, response[_S.HEALTH])
        self.assertIn(_S.STATES, response)
        self.assertIsInstance(response[_S.STATES], list)
        self.assertEquals(states, response[_S.STATES])
        self.assertIn(_S.DEVICE_TYPE_VOLTAGE, response)
        self.assertEquals(voltage, response[_S.DEVICE_TYPE_VOLTAGE])

    def _verify_vapor_http_error(self, e, http_code, message):
        """Verify the VaporHTTPError is what we expect.
        :param e: The VaporHTTPError from Synse.
        :param http_code: The expected http_code.
        :param message: The message from Synse."""
        self.assertIsInstance(e, VaporHTTPError)
        error = e.json
        self.assertIsInstance(error, dict)
        self.assertEquals(2, len(error))
        self.assertIn(_S.HTTP_CODE, error)
        self.assertEquals(http_code, error[_S.HTTP_CODE])
        self.assertIn(_S.MESSAGE, error)
        self.assertEquals(message, error[_S.MESSAGE])

    def _verify_version_snmp(self, response, version):
        """Verify the SNMP version is what we expect.
        :param response: The raw version response from Synse.
        :param version: The expected version string."""
        self.assertIsInstance(response, dict)
        self.assertEqual(version, response[_S.SNMP_VERSION])
