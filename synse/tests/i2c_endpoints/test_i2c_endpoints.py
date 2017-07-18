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
import unittest

from synse.vapor_common import http
from synse.vapor_common.errors import VaporHTTPError
from synse.vapor_common.tests.utils.strings import _S

from synse.tests.test_config import PREFIX
from synse.version import __api_version__


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
        self.assertEqual(len(boards), 15)

        for board in boards:

            self.assertIsInstance(board, dict)
            self.assertIn('board_id', board)
            self.assertIn(int(board['board_id'], 16), range(0x50010000, 0x5001000f))
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
        self.assertEqual(len(boards), 15)

        for board in boards:

            self.assertIsInstance(board, dict)
            self.assertIn('board_id', board)
            self.assertIn(int(board['board_id'], 16), range(0x50010000, 0x5001000f))
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
        self.assertEqual(len(boards), 15)

        for board in boards:

            self.assertIsInstance(board, dict)
            self.assertIn('board_id', board)
            self.assertIn(int(board['board_id'], 16), range(0x50010000, 0x5001000f))
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
        boards_scan = ["50010000", "50010001", "50010002", "50010003", "50010004", "50010005", "50010006", "50010007",
                       "50010008", "50010009", "5001000a", "5001000b", "5001000c", "5001000d", "5001000e"]

        for board_id in boards_scan:
            r = http.get(PREFIX + '/scan/rack_1/{}'.format(board_id))
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
            self.assertEqual(board['board_id'], board_id)
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
    # Test Temperature Sensor (Thermistor)
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def test_008_read_min_max(self):
        """ Test reading an I2C device.  Read min/max values out from the first temperature sensor.
        """
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

        r = http.get(PREFIX + '/read/temperature/rack_1/50010000/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['temperature_c'], 105.0)

    def test_009_read_steps_second_device(self):
        """ Test reading an I2C device.  Read from a second device and ensure values come back properly.
        """
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

        r = http.get(PREFIX + '/read/temperature/rack_1/50010001/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreaterEqual(response['temperature_c'], -7.9)
        self.assertLessEqual(response['temperature_c'], -7.7)

    def test_010_read_single_value(self):
        """ Test reading an I2C device.  Read single value repeatedly out from the fourth temperature sensor.
        """
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
        r = http.get(PREFIX + '/read/temperature/rack_1/50010000/CEC Temperature 1 - min-max')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['temperature_c'], -7.80377)

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

    # endregion

    # region Test Pressure Sensor
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Test Pressure Sensor
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def test_014_read_min_max(self):
        """ Test reading an I2C device.  Read min/max values out from the first temperature sensor.
        """
        r = http.get(PREFIX + '/read/pressure/rack_1/50010005/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertEqual(response[_S.PRESSURE_PA], 0.0)

        r = http.get(PREFIX + '/read/pressure/rack_1/50010005/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertEqual(response[_S.PRESSURE_PA], -1.0)

        r = http.get(PREFIX + '/read/pressure/rack_1/50010005/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertEqual(response[_S.PRESSURE_PA], 0.0)

    def test_015_read_steps_second_device(self):
        """ Test reading an I2C device.  Read from a second device and ensure values come back properly.
        """
        r = http.get(PREFIX + '/read/pressure/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertGreaterEqual(response[_S.PRESSURE_PA], 0.9)
        self.assertLessEqual(response[_S.PRESSURE_PA], 1.0)

        r = http.get(PREFIX + '/read/pressure/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertGreaterEqual(response[_S.PRESSURE_PA], 254.9)
        self.assertLessEqual(response[_S.PRESSURE_PA], 255.1)

        r = http.get(PREFIX + '/read/pressure/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertGreaterEqual(response[_S.PRESSURE_PA], 16383.9)
        self.assertLessEqual(response[_S.PRESSURE_PA], 16384.1)

        r = http.get(PREFIX + '/read/pressure/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertGreaterEqual(response[_S.PRESSURE_PA], 32766.9)
        self.assertLessEqual(response[_S.PRESSURE_PA], 32767.1)

        r = http.get(PREFIX + '/read/pressure/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertGreaterEqual(response[_S.PRESSURE_PA], -32700.1)
        self.assertLessEqual(response[_S.PRESSURE_PA], -32699.9)

        r = http.get(PREFIX + '/read/pressure/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertGreaterEqual(response[_S.PRESSURE_PA], 2558.9)
        self.assertLessEqual(response[_S.PRESSURE_PA], 2559.1)

        r = http.get(PREFIX + '/read/pressure/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertGreaterEqual(response[_S.PRESSURE_PA], -86.1)
        self.assertLessEqual(response[_S.PRESSURE_PA], -85.9)

        r = http.get(PREFIX + '/read/pressure/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertGreaterEqual(response[_S.PRESSURE_PA], -256.1)
        self.assertLessEqual(response[_S.PRESSURE_PA], -255.9)

        r = http.get(PREFIX + '/read/pressure/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertGreaterEqual(response[_S.PRESSURE_PA], 0.9)
        self.assertLessEqual(response[_S.PRESSURE_PA], 1.0)

        r = http.get(PREFIX + '/read/pressure/rack_1/50010006/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertGreaterEqual(response[_S.PRESSURE_PA], 254.9)
        self.assertLessEqual(response[_S.PRESSURE_PA], 255.1)

    def test_016_read_single_value(self):
        """ Test reading an I2C device.  Read single value repeatedly out from the fourth temperature sensor.
        """
        r = http.get(PREFIX + '/read/pressure/rack_1/50010007/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertEqual(response[_S.PRESSURE_PA], 0.0)

        r = http.get(PREFIX + '/read/pressure/rack_1/50010007/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertEqual(response[_S.PRESSURE_PA], 0.0)

    def test_017_read_bad_device(self):
        """ Test reading an I2C device.  This device has no emulator behind it, so should raise 500.
        """
        # no values from emulator
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/pressure/rack_1/50010008/0001')

        # no emulator backing
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/pressure/rack_1/50010009/0001')

        # non-existent board
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/pressure/rack_1/50000040/0001')

        # good board, bad device
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/pressure/rack_1/50010006/0002')

    def test_018_read_min_max_by_name(self):
        """ Test reading an I2C device.  Read min/max values out from the first temperature sensor by name.
        """
        r = http.get(PREFIX + '/read/pressure/rack_1/50010005/CEC Pressure 1 - min-max')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertEqual(response[_S.PRESSURE_PA], -1.0)

        r = http.get(PREFIX + '/read/pressure/rack_1/50010005/CEC Pressure 1 - min-max')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertEqual(response[_S.PRESSURE_PA], 0.0)

        r = http.get(PREFIX + '/read/pressure/rack_1/50010005/CEC Pressure 1 - min-max')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.PRESSURE_PA, response)
        self.assertIsInstance(response[_S.PRESSURE_PA], float)
        self.assertEqual(response[_S.PRESSURE_PA], -1.0)

    def test_019_read_invalid_device_type_or_command(self):
        """ Test reading an I2C device.  Read wrong type of device, or use wrong command.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/humidity/rack_1/50010005/CEC Pressure 1 - min-max')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/humidity/rack_1/50010005/0001')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/power/rack_1/50010005/0001')

    def test_206_read_pressure_version(self):
        """
        Test version command on a pressure sensor.
        """
        r = http.get(PREFIX + '/version/rack_1/50010005')
        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual('Synse I2C Bridge v1.0', response['firmware_version'])

    # endregion

    # region Test LED Control
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Test LED Control
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def test_020_read_single_valid(self):
        """ Test reading an I2C device.  Read a single valid value.
        """
        r = http.get(PREFIX + '/read/led/rack_1/5001000a/0001')
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

        r = http.get(PREFIX + '/led/rack_1/5001000a/0001')
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

    def test_021_read_steps_second_device(self):
        """ Test reading an I2C device.  Read from a second device and ensure values come back properly.
        """
        r = http.get(PREFIX + '/led/rack_1/5001000b/0001')
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

        r = http.get(PREFIX + '/led/rack_1/5001000b/0001')
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

        r = http.get(PREFIX + '/led/rack_1/5001000b/0001')
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

        r = http.get(PREFIX + '/led/rack_1/5001000b/0001')
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

    def test_022_read_write(self):
        """ Test reading and writing an I2C device.
        """
        # first read what's there
        r = http.get(PREFIX + '/led/rack_1/5001000c/0001')
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
        self.assertEqual(response['led_color'], "000000")
        self.assertEqual(response['blink_state'], "steady")

        # then set and read back values x 3... [0]
        r = http.get(PREFIX + '/led/rack_1/5001000c/0001/on/ffffff/steady')
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

        r = http.get(PREFIX + '/led/rack_1/5001000c/0001')
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

        # [1]
        r = http.get(PREFIX + '/led/rack_1/5001000c/0001/on/0beef0/blink')
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
        self.assertEqual(response['led_color'], "0beef0")
        self.assertEqual(response['blink_state'], "blink")

        r = http.get(PREFIX + '/led/rack_1/5001000c/0001')
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
        self.assertEqual(response['led_color'], "0beef0")
        self.assertEqual(response['blink_state'], "blink")

        # [2]
        r = http.get(PREFIX + '/led/rack_1/5001000c/0001/off/7ac055/blink')
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
        self.assertEqual(response['led_color'], "7ac055")
        self.assertEqual(response['blink_state'], "steady")

        r = http.get(PREFIX + '/led/rack_1/5001000c/0001')
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
        self.assertEqual(response['led_color'], "7ac055")
        self.assertEqual(response['blink_state'], "steady")

    def test_023_bad_command_writes(self):
        """ Send bad commands to LED and make sure it does not let anything through.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/5001000a/0001/on')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/5001000a/0001/on/000000')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/5001000a/0001/on/blink')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/5001000a/0001/blink/000000')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/5001000a/0001/blink/000000/on')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/5001000a/0001/on/999999/blank')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/5001000a/0001/onn/888888/blink')

        # ensure we have not had any bad things happen to our device
        r = http.get(PREFIX + '/read/led/rack_1/5001000a/0001')
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

    def test_024_read_bad_device(self):
        """ Test reading a bad I2C device.  This device has no emulator behind it, so should raise 500.
        """
        # no values from emulator
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/led/rack_1/5001000d/0001')

        # no emulator backing
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/led/rack_1/5001000e/0001')

        # non-existent board
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/led/rack_1/50000040/0001')

        # good board, bad device
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/led/rack_1/5001000c/0002')

        # no values from emulator
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/5001000d/0001')

        # no emulator backing
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/5001000e/0001')

        # non-existent board
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/50000040/0001')

        # good board, bad device
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/led/rack_1/5001000a/0002')

    def test_025_read_one_valid_by_name(self):
        """ Test reading an I2C device.  Read valid values out from the first led controller by name.
        """
        r = http.get(PREFIX + '/read/led/rack_1/5001000a/Rack LED - steady-white')
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

    def test_026_read_invalid_device_type_or_command(self):
        """ Test reading an I2C device.  Read wrong type of device, or use wrong command.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/humidity/rack_1/5001000a/Rack LED - steady-white')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/humidity/rack_1/5001000a/0001')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/power/rack_1/5001000a/0001')

    def test_307_read_led_version(self):
        """
        Test version command on an LED.
        """
        r = http.get(PREFIX + '/version/rack_1/5001000a')
        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual('Synse I2C Bridge v1.0', response['firmware_version'])

    # endregion
