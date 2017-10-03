#!/usr/bin/env python
""" Synse I2C Endpoint Tests

    Author: Andrew Cencini
    Date:   10/19/2016

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
import json
import logging
import unittest

from synse.tests.test_config import PREFIX
from synse.vapor_common import http
from synse.vapor_common.errors import VaporHTTPError
from synse.vapor_common.tests.utils.strings import _S
from synse.version import __api_version__

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------------------------
# Difficulties with these tests:
# The emulator passes out data based on the device channel which is in the Synse configuration.
# Synse passes out board ids which are not in the Synse configuration.
# The device channel is not passed out on a Synse scan.
#
# When devices are added to the Synse configuration but not at the end of the configuration file,
# board ids for subsequent devices will change.
#
# For now: Please document the device channel for each test URL.
# This makes it much easier to update the test URLs when the board id changes.
# ---------------------------------------------------------------------------------------------

# -----------------------------------
# Board id : channel : device_info:
# -----------------------------------
# 50010000: 0000: CEC Temperature 1 - min-max
# 50010001: 0001: CEC Temperature 2 - steps
# 50010002: 0002: CEC Temperature 3 - bad-device (no emulator data)
# 50010003: 0003: CEC Temperature 4 - one-value
# 50010004: 0004: CEC Temperature 5 - no-device (channel not in emulator data)
# 50010005: 0020: CEC Temperature 1b - min-max
# 50010006: 0021: CEC Temperature 2b - steps
# 50010007: 0022: CEC Temperature 3b - bad-device (no emulator data)
# 50010008: 0023: CEC Temperature 4b - one-value
# 50010009: 0024: CEC Temperature 5b - no-device (channel not in emulator data)
# 5001000a: 0008: CEC Pressure 1 - min-max
# 5001000b: 0009: CEC Pressure 2 - steps
# 5001000c: 000a: CEC Pressure 3 - one-value
# 5001000d: 000b: CEC Pressure 4 - no-data (no emulator data)
# 5001000e: ffff: CEC Pressure 5 - no-device (channel not in emulator data)
# 5001000f: 0014: Rack LED - steady-white
# 50010010: 0015: Rack LED - cycle-on-blink-off
# 50010011: 0016: Rack LED - read-write
# 50010012: 0017: Rack LED - no-data (no emulator data)
# 50010013: ffff: Rack LED - no-device (channel not in emulator data)


class I2CEndpointsTestCase(unittest.TestCase):
    """ I2C Endpoint tests test hitting Synse endpoints with only I2C
    devices configured, with the I2C emulator running.
    """

    # region General I2C tests
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
        self.assertEqual(len(boards), 20)

        for board in boards:

            self.assertIsInstance(board, dict)
            self.assertIn('board_id', board)
            self.assertIn(int(board['board_id'], 16), range(0x50010000, 0x50010014))  # 0 to 0x13 -> 20 i2c devices
            self.assertIn('devices', board)

            devices = board['devices']
            self.assertIsInstance(devices, list)
            self.assertEqual(len(devices), 1)

            device_types = [
                'temperature', 'pressure', 'vapor_led'
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
        self.assertEqual(len(boards), 20)

        for board in boards:

            self.assertIsInstance(board, dict)
            self.assertIn('board_id', board)
            self.assertIn(int(board['board_id'], 16), range(0x50010000, 0x50010014))  # 0 to 0x13 -> 20 i2c devices
            self.assertIn('devices', board)

            devices = board['devices']
            self.assertIsInstance(devices, list)
            self.assertEqual(len(devices), 1)

            device_types = [
                'temperature', 'pressure', 'vapor_led'
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
        self.assertEqual(len(boards), 20)

        for board in boards:

            self.assertIsInstance(board, dict)
            self.assertIn('board_id', board)
            self.assertIn(int(board['board_id'], 16), range(0x50010000, 0x50010014))  # 0 to 0x13 -> 20 i2c devices
            self.assertIn('devices', board)

            devices = board['devices']
            self.assertIsInstance(devices, list)
            self.assertEqual(len(devices), 1)

            device_types = [
                'temperature', 'pressure', 'vapor_led'
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
        int_boards = range(0x50010000, 0x50010014)  # Board ids we should pick up on the scan. (max 0x50010013)
        boards_scan = ['{:08x}'.format(x) for x in int_boards]  # Convert to hex string.

        for board_id in boards_scan:
            # Scan by rack and board_id.
            r = http.get(PREFIX + '/scan/rack_1/{}'.format(board_id))
            self.assertTrue(http.request_ok(r.status_code))

            # Make sure we get boards.
            response = r.json()
            self.assertIsInstance(response, dict)
            self.assertIn('boards', response)

            # Make sure boards is a list of length 1.
            boards = response['boards']
            self.assertIsInstance(boards, list)
            self.assertEqual(len(boards), 1)

            # Make sure board_id and devices fields are in the scan. Check board_id is in boards_scan.
            board = boards[0]
            self.assertIsInstance(board, dict)
            self.assertIn('board_id', board)
            self.assertEqual(board['board_id'], board_id)
            self.assertIn('devices', board)

            # Make sure devices is a list of length 1.
            devices = board['devices']
            self.assertIsInstance(devices, list)
            self.assertEqual(len(devices), 1)

            device_types = [
                'temperature', 'pressure', 'vapor_led'
            ]

            for device in devices:
                # Make sure device is a dict and expected fields are there.
                self.assertIsInstance(device, dict)
                self.assertIn('device_type', device)
                self.assertIn('device_id', device)
                self.assertIn('device_info', device)

                # Make sure device_type is one we expect.
                dev_type = device['device_type']
                self.assertIn(dev_type.lower(), device_types)

    def test_006_board_id_does_not_exist(self):
        """
        Test the version command on a board that does not exist.
        """
        try:
            http.get(PREFIX + '/version/rack_1/board_id_does_not_exist')
            self.fail("Expected VaporHTTPError on board id that does not exist")
        except VaporHTTPError as error:
            # FUTURE: (REST) This should return 404 (not found) since there is nothing at the URI.
            # This is a client side error and not an internal server error.
            response = error.response
            self.assertEqual(500, response.status_code)
            json = response.json()
            self.assertEqual(500, json['http_code'])
            self.assertEqual(
                'Board ID (board_id_does_not_exist) not associated with any registered devicebus handler.',
                json['message'])

    # endregion

    # region Test Temperature Sensor (Thermistor)
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Test Temperature Sensor (max11608 Thermistor)
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def test_008_read_min_max(self):
        """ Test reading an I2C device.  Read min/max values out from the first temperature sensor.
        """
        # The board id 50010000 is using channel 0000 (emulator data).
        r = http.get(PREFIX + '/read/temperature/rack_1/50010000/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['temperature_c'], 105.0)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010000/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['temperature_c'], -7.80377)

    def test_009_read_steps_second_device(self):
        """ Test reading an I2C device.  Read from a second device and ensure values come back properly.
        """
        # The board id 50010001 is using channel 0001 (emulator data).
        r = http.get(PREFIX + '/read/temperature/rack_1/50010001/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], -7.9)
        self.assertLessEqual(response['temperature_c'], -7.7)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010001/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 18.0)
        self.assertLessEqual(response['temperature_c'], 18.6)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010001/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 17.9)
        self.assertLessEqual(response['temperature_c'], 18.0)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010001/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 18.5)
        self.assertLessEqual(response['temperature_c'], 18.8)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010001/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 37.9)
        self.assertLessEqual(response['temperature_c'], 38.1)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010001/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 38.4)
        self.assertLessEqual(response['temperature_c'], 38.5)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010001/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 52.8)
        self.assertLessEqual(response['temperature_c'], 53.0)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010001/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 66.9)
        self.assertLessEqual(response['temperature_c'], 67.1)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010001/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 67.5)
        self.assertLessEqual(response['temperature_c'], 67.6)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010001/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 79.5)
        self.assertLessEqual(response['temperature_c'], 80.0)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010001/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 80.5)
        self.assertLessEqual(response['temperature_c'], 80.7)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010001/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 93.9)
        self.assertLessEqual(response['temperature_c'], 94.2)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010001/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 94.9)
        self.assertLessEqual(response['temperature_c'], 95.1)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010001/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 104.9)
        self.assertLessEqual(response['temperature_c'], 105.1)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010001/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 104.9)
        self.assertLessEqual(response['temperature_c'], 105.1)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010001/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 104.9)
        self.assertLessEqual(response['temperature_c'], 105.1)

    def test_010_read_single_value(self):
        """ Test reading an I2C device.  Read single value repeatedly out from the fourth temperature sensor.
        """
        # The board id 50010003 is using channel 0003 (emulator data).
        r = http.get(PREFIX + '/read/temperature/rack_1/50010003/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['temperature_c'], 18.0)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010003/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['temperature_c'], 18.0)

    def test_011_read_bad_device(self):
        """ Test reading an I2C device.  This device has no emulator behind it, so should raise 500.
        """
        # The board id 50010002 is using channel 0002 (emulator data).
        # The board id 50010004 is using channel 0004 (emulator data).
        # no values from emulator
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/temperature/rack_1/50010002/0001')

        # no emulator backing
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/temperature/rack_1/50010004/0001')

        # non-existent board
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/temperature/rack_1/50000040/0001')

        # good board, bad device
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/temperature/rack_1/50010000/0002')

    def test_012_read_min_max_by_name(self):
        """ Test reading an I2C device.  Read min/max values out from the first temperature sensor by name.
        """
        # The board id 50010000 is using channel 0000 (emulator data).
        r = http.get(PREFIX + '/read/temperature/rack_1/50010000/CEC Temperature 1 - min-max')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['temperature_c'], 105.0)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010000/CEC Temperature 1 - min-max')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['temperature_c'], -7.80377)

    def test_013_read_invalid_device_type_or_command(self):
        """ Test reading an I2C device.  Read wrong type of device, or use wrong command.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/humidity/rack_1/50010000/CEC Temperature 1 - min-max')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/humidity/rack_1/50010000/0001')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/power/rack_1/50010000/0001')

    def test_106_read_thermistor_version(self):
        """
        Test version command on a thermistor.
        """
        r = http.get(PREFIX + '/version/rack_1/50010000')
        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual('Synse I2C Bridge v1.0', response['firmware_version'])

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Test Temperature Sensor (max11610 Thermistor)
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def test_014_read_min_max(self):
        """ Test reading an I2C device.  Read min/max values out from the first temperature sensor.
        """
        # The board id 50010005 is using channel 0020 (emulator data).
        r = http.get(PREFIX + '/read/temperature/rack_1/50010005/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['temperature_c'], 105.0)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010005/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['temperature_c'], -7.80377)

    def test_015_read_steps_second_device(self):
        """ Test reading an I2C device.  Read from a second device and ensure values come back properly.
        """
        # The board id 50010006 is using channel 0021 (emulator data).
        r = http.get(PREFIX + '/read/temperature/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], -7.9)
        self.assertLessEqual(response['temperature_c'], -7.7)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 17.9)
        self.assertLessEqual(response['temperature_c'], 18.1)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 17.9)
        self.assertLessEqual(response['temperature_c'], 18.0)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 18.5)
        self.assertLessEqual(response['temperature_c'], 18.6)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 37.9)
        self.assertLessEqual(response['temperature_c'], 38.1)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 38.4)
        self.assertLessEqual(response['temperature_c'], 38.5)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 52.9)
        self.assertLessEqual(response['temperature_c'], 53.1)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 66.9)
        self.assertLessEqual(response['temperature_c'], 67.1)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 67.5)
        self.assertLessEqual(response['temperature_c'], 67.6)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 79.9)
        self.assertLessEqual(response['temperature_c'], 80.1)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 80.6)
        self.assertLessEqual(response['temperature_c'], 80.7)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 93.9)
        self.assertLessEqual(response['temperature_c'], 94.1)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], 94.9)
        self.assertLessEqual(response['temperature_c'], 95.1)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['temperature_c'], 105.0)  # at max

        r = http.get(PREFIX + '/read/temperature/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['temperature_c'], 105.0)  # at max

        r = http.get(PREFIX + '/read/temperature/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['temperature_c'], 105.0)  # at max

    def test_016_read_single_value(self):
        """ Test reading an I2C device.  Read single value repeatedly out from the fourth temperature sensor.
        """
        # The board id 50010008 is using channel 0023 (emulator data).
        r = http.get(PREFIX + '/read/temperature/rack_1/50010008/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['temperature_c'], 18.0)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010008/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['temperature_c'], 18.0)

    def test_017_read_bad_device(self):
        """ Test reading an I2C device.  This device has no emulator behind it, so should raise 500.
        """
        # The board id 50010007 is using channel 0022 (emulator data).
        # The board id 50010009 is using channel 0024 (emulator data).
        # no values from emulator
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/temperature/rack_1/50010007/0001')

        # no emulator backing
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/temperature/rack_1/50010009/0001')

        # non-existent board
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/temperature/rack_1/50000040/0001')

        # good board, bad device
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/temperature/rack_1/50010005/0002')

    def test_018_read_min_max_by_name(self):
        """ Test reading an I2C device.  Read min/max values out from the first temperature sensor by name.
        """
        # The board id 50010005 is using channel 0020 (emulator data).
        r = http.get(PREFIX + '/read/temperature/rack_1/50010005/CEC Temperature 1b - min-max')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['temperature_c'], 105.0)

        r = http.get(PREFIX + '/read/temperature/rack_1/50010005/CEC Temperature 1b - min-max')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['temperature_c'], -7.80377)

    def test_019_read_invalid_device_type_or_command(self):
        """ Test reading an I2C device.  Read wrong type of device, or use wrong command.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/humidity/rack_1/50010005/CEC Temperature 1 - min-max')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/humidity/rack_1/50010005/0001')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/power/rack_1/50010005/0001')

    def test_107_read_thermistor_version(self):
        """
        Test version command on a thermistor.
        """
        r = http.get(PREFIX + '/version/rack_1/50010005')
        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual('Synse I2C Bridge v1.0', response['firmware_version'])

    # endregion

    # region Test Pressure Sensor
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Test Pressure Sensor
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def test_020_read_min_max(self):
        """ Test reading an I2C device.  Read min/max values out from the first temperature sensor.
        """
        r = http.get(PREFIX + '/read/pressure/rack_1/5001000a/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertEqual(response[_S.PRESSURE_PA], 0.0)

        r = http.get(PREFIX + '/read/pressure/rack_1/5001000a/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertEqual(response[_S.PRESSURE_PA], -1.0)

    def test_021_read_steps_second_device(self):
        """ Test reading an I2C device.  Read from a second device and ensure values come back properly.
        """
        # The board id 5001000b is using channel 0009 (emulator data).
        r = http.get(PREFIX + '/read/pressure/rack_1/5001000b/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertGreaterEqual(response[_S.PRESSURE_PA], 0.9)
        self.assertLessEqual(response[_S.PRESSURE_PA], 1.0)

        r = http.get(PREFIX + '/read/pressure/rack_1/5001000b/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertGreaterEqual(response[_S.PRESSURE_PA], 254.9)
        self.assertLessEqual(response[_S.PRESSURE_PA], 255.1)

        r = http.get(PREFIX + '/read/pressure/rack_1/5001000b/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertGreaterEqual(response[_S.PRESSURE_PA], 16383.9)
        self.assertLessEqual(response[_S.PRESSURE_PA], 16384.1)

        r = http.get(PREFIX + '/read/pressure/rack_1/5001000b/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertGreaterEqual(response[_S.PRESSURE_PA], 32766.9)
        self.assertLessEqual(response[_S.PRESSURE_PA], 32767.1)

        r = http.get(PREFIX + '/read/pressure/rack_1/5001000b/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertGreaterEqual(response[_S.PRESSURE_PA], -32700.1)
        self.assertLessEqual(response[_S.PRESSURE_PA], -32699.9)

        r = http.get(PREFIX + '/read/pressure/rack_1/5001000b/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertGreaterEqual(response[_S.PRESSURE_PA], 2558.9)
        self.assertLessEqual(response[_S.PRESSURE_PA], 2559.1)

        r = http.get(PREFIX + '/read/pressure/rack_1/5001000b/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertGreaterEqual(response[_S.PRESSURE_PA], -86.1)
        self.assertLessEqual(response[_S.PRESSURE_PA], -85.9)

        r = http.get(PREFIX + '/read/pressure/rack_1/5001000b/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertGreaterEqual(response[_S.PRESSURE_PA], -256.1)
        self.assertLessEqual(response[_S.PRESSURE_PA], -255.9)

    def test_022_read_single_value(self):
        """ Test reading an I2C device.  Read single value repeatedly out from the fourth temperature sensor.
        """
        # The board id 5001000c is using channel 000a (emulator data).
        r = http.get(PREFIX + '/read/pressure/rack_1/5001000c/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertEqual(response[_S.PRESSURE_PA], 0.0)

        r = http.get(PREFIX + '/read/pressure/rack_1/5001000c/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertEqual(response[_S.PRESSURE_PA], 0.0)

    def test_023_read_bad_device(self):
        """ Test reading an I2C device.  This device has no emulator behind it, so should raise 500.
        """
        # The board id 5001000d is using channel 000b (emulator data).
        # The board id 5001000e is using channel ffff (emulator data).
        # no values from emulator
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/pressure/rack_1/5001000d/0001')

        # no emulator backing
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/pressure/rack_1/5001000e/0001')

        # non-existent board
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/pressure/rack_1/50000040/0001')

        # good board, bad device
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/pressure/rack_1/5001000b/0002')

    def test_024_read_min_max_by_name(self):
        """ Test reading an I2C device.  Read min/max values out from the first temperature sensor by name.
        """
        # The board id 5001000a is using channel 0008 (emulator data).
        r = http.get(PREFIX + '/read/pressure/rack_1/5001000a/CEC Pressure 1 - min-max')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertEqual(response[_S.PRESSURE_PA], 0.0)

        r = http.get(PREFIX + '/read/pressure/rack_1/5001000a/CEC Pressure 1 - min-max')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertEqual(response[_S.PRESSURE_PA], -1.0)

    def test_025_read_invalid_device_type_or_command(self):
        """ Test reading an I2C device.  Read wrong type of device, or use wrong command.
        """
        # The board id 5001000a is using channel 0008 (emulator data).
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/humidity/rack_1/5001000a/CEC Pressure 1 - min-max')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/humidity/rack_1/5001000a/0001')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/power/rack_1/5001000a/0001')

    def test_206_read_pressure_version(self):
        """
        Test version command on a pressure sensor.
        """
        r = http.get(PREFIX + '/version/rack_1/5001000a')
        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual('Synse I2C Bridge v1.0', response['firmware_version'])

    # endregion

    # region Test LED Control
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Test LED Control
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def test_026_read_single_valid(self):
        """ Test reading an I2C device.  Read a single valid value.
        """
        # The board id 5001000f is using channel 0014 (emulator data).
        r = http.get(PREFIX + '/read/led/rack_1/5001000f/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertIn('blink_state', response)
        self.assertIn('led_color', response)
        self.assertIsInstance(response['led_state'], basestring)
        self.assertIsInstance(response['blink_state'], basestring)
        self.assertIsInstance(response['led_color'], basestring)
        self.assertEqual(response['led_state'], "on")
        self.assertEqual(response['led_color'], "ffffff")
        self.assertEqual(response['blink_state'], "steady")

        r = http.get(PREFIX + '/read/led/rack_1/5001000f/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertIn('blink_state', response)
        self.assertIn('led_color', response)
        self.assertIsInstance(response['led_state'], basestring)
        self.assertIsInstance(response['blink_state'], basestring)
        self.assertIsInstance(response['led_color'], basestring)
        self.assertEqual(response['led_state'], "on")
        self.assertEqual(response['led_color'], "ffffff")
        self.assertEqual(response['blink_state'], "steady")

    def test_027_read_steps_second_device(self):
        """ Test reading an I2C device.  Read from a second device and ensure values come back properly.
        """
        # The board id 50010010 is using channel 0015 (emulator data).
        r = http.get(PREFIX + '/led/rack_1/50010010/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertIn('blink_state', response)
        self.assertIn('led_color', response)
        self.assertIsInstance(response['led_state'], basestring)
        self.assertIsInstance(response['blink_state'], basestring)
        self.assertIsInstance(response['led_color'], basestring)
        self.assertEqual(response['led_state'], "off")
        self.assertEqual(response['led_color'], "ffffff")
        self.assertEqual(response['blink_state'], "steady")

        r = http.get(PREFIX + '/led/rack_1/50010010/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertIn('blink_state', response)
        self.assertIn('led_color', response)
        self.assertIsInstance(response['led_state'], basestring)
        self.assertIsInstance(response['blink_state'], basestring)
        self.assertIsInstance(response['led_color'], basestring)
        self.assertEqual(response['led_state'], "on")
        self.assertEqual(response['led_color'], "ffffff")
        self.assertEqual(response['blink_state'], "steady")

        r = http.get(PREFIX + '/led/rack_1/50010010/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('led_state', response)
        self.assertIn('blink_state', response)
        self.assertIn('led_color', response)
        self.assertIsInstance(response['led_state'], basestring)
        self.assertIsInstance(response['blink_state'], basestring)
        self.assertIsInstance(response['led_color'], basestring)
        self.assertEqual(response['led_state'], "on")
        self.assertEqual(response['led_color'], "ffffff")
        self.assertEqual(response['blink_state'], "blink")

    def test_030_read_bad_device(self):
        """ Test reading a bad I2C device.  This device has no emulator behind it, so should raise 500.
        """
        # The board id 50010012 is using channel 0017 (emulator data).
        # The board id 50010013 is using channel ffff (emulator data).
        # no values from emulator
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/led/rack_1/50010012/0001')

        # no emulator backing
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/led/rack_1/50010013/0001')

        # non-existent board
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/led/rack_1/50000040/0001')

        # good board, bad device (pressure)
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/led/rack_1/5001000c/0002')

        # no values from emulator
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/50010012/0001')

        # no emulator backing
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/50010013/0001')

        # non-existent board
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/50000040/0001')

        # good board, bad device
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/5001000f/0002')

    def test_032_read_invalid_device_type_or_command(self):
        """ Test reading an I2C device.  Read wrong type of device, or use wrong command.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/humidity/rack_1/5001000f/Rack LED - steady-white')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/humidity/rack_1/5001000f/0001')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/power/rack_1/5001000f/0001')

    def test_307_read_led_version(self):
        """
        Test version command on an LED.
        """
        # The board id 5001000f is using channel 0014 (emulator data).
        r = http.get(PREFIX + '/version/rack_1/5001000f')
        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual('Synse I2C Bridge v1.0', response['firmware_version'])

    # endregion
