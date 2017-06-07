#!/usr/bin/env python
""" Synse RS485 Endpoint Tests

    Author: Andrew Cencini
    Date:   10/12/2016

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
from vapor_common.tests.utils.strings import _S


class Rs485EndpointsTestCase(unittest.TestCase):
    """ RS485 Endpoint tests test hitting Synse endpoints with only RS485
    devices configured, with the RS485 emulator running.
    """

    # region General Endpoint Tests.
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
        self.assertEqual(len(boards), 10)

        for board in boards:

            self.assertIsInstance(board, dict)
            self.assertIn('board_id', board)
            self.assertIn(int(board['board_id'], 16), range(0x50000000, 0x5000000a))
            self.assertIn('devices', board)

            devices = board['devices']
            self.assertIsInstance(devices, list)
            self.assertEqual(len(devices), 1)

            device_types = [
                'humidity', 'airflow', 'vapor_fan'
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
        self.assertEqual(len(boards), 10)

        for board in boards:

            self.assertIsInstance(board, dict)
            self.assertIn('board_id', board)
            self.assertIn(int(board['board_id'], 16), range(0x50000000, 0x5000000a))
            self.assertIn('devices', board)

            devices = board['devices']
            self.assertIsInstance(devices, list)
            self.assertEqual(len(devices), 1)

            device_types = [
                'humidity', 'airflow', 'vapor_fan'
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
        self.assertEqual(len(boards), 10)

        for board in boards:

            self.assertIsInstance(board, dict)
            self.assertIn('board_id', board)
            self.assertIn(int(board['board_id'], 16), range(0x50000000, 0x5000000a))
            self.assertIn('devices', board)

            devices = board['devices']
            self.assertIsInstance(devices, list)
            self.assertEqual(len(devices), 1)

            device_types = [
                'humidity', 'airflow', 'vapor_fan'
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
        boards_scan = ["50000000", "50000001", "50000002", "50000003", "50000004", "50000005", "50000006", "50000007",
                       "50000008", "50000009"]
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
                'humidity', 'airflow', 'vapor_fan'
            ]

            for device in devices:
                self.assertIsInstance(device, dict)
                self.assertIn('device_type', device)
                self.assertIn('device_id', device)

                dev_type = device['device_type']
                self.assertIn(dev_type.lower(), device_types)

    def test_008_board_id_does_not_exist(self):
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

    # region Test Humidity Sensor
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Test Humidity Sensor
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def test_009_read_min_max(self):
        """ Test reading an RS485 device.  Read min/max values out from the first humidity sensor.
        """
        r = http.get(PREFIX + '/read/humidity/rack_1/50000000/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('humidity', response)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['humidity'], float)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['humidity'], 0.0)
        self.assertEqual(response['temperature_c'], -45.0)

        r = http.get(PREFIX + '/read/humidity/rack_1/50000000/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('humidity', response)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['humidity'], float)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['humidity'], 100.0)
        self.assertEqual(response['temperature_c'], 130.0)

        r = http.get(PREFIX + '/read/humidity/rack_1/50000000/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('humidity', response)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['humidity'], float)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['humidity'], 0.0)
        self.assertEqual(response['temperature_c'], -45.0)

    def test_010_read_midrange_second_device(self):
        """ Test reading an RS485 device.  Read from a second device and ensure values come back properly.
        """
        r = http.get(PREFIX + '/read/humidity/rack_1/50000001/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('humidity', response)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['humidity'], float)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertGreater(response['humidity'], 25.0)
        self.assertLess(response['humidity'], 25.1)
        self.assertGreater(response['temperature_c'], 42.5)
        self.assertLess(response['temperature_c'], 42.6)

        r = http.get(PREFIX + '/read/humidity/rack_1/50000001/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('humidity', response)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['humidity'], float)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['humidity'], 100.0)
        self.assertEqual(response['temperature_c'], 130.0)

        r = http.get(PREFIX + '/read/humidity/rack_1/50000001/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('humidity', response)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['humidity'], float)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['humidity'], 0.0)
        self.assertEqual(response['temperature_c'], -45.0)

    def test_011_read_bad_device(self):
        """ Test reading an RS485 device.  This device has no registers behind it, so should raise 500.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/humidity/rack_1/50000002/0001')

        # non-existent board
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/humidity/rack_1/50000040/0001')

        # good board, bad device
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/humidity/rack_1/50000000/0002')

    def test_012_read_min_max_by_name(self):
        """ Test reading an RS485 device.  Read min/max values out from the first humidity sensor by name.
        """
        r = http.get(PREFIX + '/read/humidity/rack_1/50000000/cec humidity 1')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('humidity', response)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['humidity'], float)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['humidity'], 100.0)
        self.assertEqual(response['temperature_c'], 130.0)

        r = http.get(PREFIX + '/read/humidity/rack_1/50000000/cec humidity 1')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('humidity', response)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['humidity'], float)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['humidity'], 0.0)
        self.assertEqual(response['temperature_c'], -45.0)

        r = http.get(PREFIX + '/read/humidity/rack_1/50000000/cec humidity 1')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('humidity', response)
        self.assertIn('temperature_c', response)
        self.assertIsInstance(response['humidity'], float)
        self.assertIsInstance(response['temperature_c'], float)
        self.assertEqual(response['humidity'], 100.0)
        self.assertEqual(response['temperature_c'], 130.0)

    def test_013_read_invalid_device_type_or_command(self):
        """ Test reading an RS485 device.  Read wrong type of device, or use wrong command.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/temperature/rack_1/50000000/cec humidity 1')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/temperature/rack_1/50000000/0001')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/power/rack_1/50000000/0001')

    def test_014_read_humidity_version(self):
        """
        Test version command on humidity sensor.
        """
        r = http.get(PREFIX + '/version/rack_1/50000000')
        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(
            'Synse RS-485 Bridge v1.0', response['firmware_version'])

    # endregion

    # region Test Airflow Sensor
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Test Airflow Sensor
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def test_015_read_min_max(self):
        """ Test reading an RS485 device.  Read min/max values out from the second airflow sensor.
        """
        r = http.get(PREFIX + '/read/airflow/rack_1/50000004/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.AIRFLOW_MILLIMETERS_PER_SECOND, response)
        self.assertIsInstance(response[_S.AIRFLOW_MILLIMETERS_PER_SECOND], int)
        self.assertEqual(response[_S.AIRFLOW_MILLIMETERS_PER_SECOND], 0)

        r = http.get(PREFIX + '/read/airflow/rack_1/50000004/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.AIRFLOW_MILLIMETERS_PER_SECOND, response)
        self.assertIsInstance(response[_S.AIRFLOW_MILLIMETERS_PER_SECOND], int)
        self.assertEqual(response[_S.AIRFLOW_MILLIMETERS_PER_SECOND], 399)

        r = http.get(PREFIX + '/read/airflow/rack_1/50000004/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.AIRFLOW_MILLIMETERS_PER_SECOND, response)
        self.assertIsInstance(response[_S.AIRFLOW_MILLIMETERS_PER_SECOND], int)
        self.assertEqual(response[_S.AIRFLOW_MILLIMETERS_PER_SECOND], 0)

    def test_016_read_steps(self):
        """ Test reading an RS485 device.  Read set of steps.
        """

        target_readings = [0, 94, 95, 223, 224, 325, 326, 373, 374, 399]

        for x in range(0, 10):
            r = http.get(PREFIX + '/read/airflow/rack_1/50000003/0001')
            self.assertTrue(http.request_ok(r.status_code))

            response = r.json()
            self.assertIsInstance(response, dict)
            self.assertIn(_S.AIRFLOW_MILLIMETERS_PER_SECOND, response)
            self.assertIsInstance(response[_S.AIRFLOW_MILLIMETERS_PER_SECOND], int)
            self.assertEqual(response[_S.AIRFLOW_MILLIMETERS_PER_SECOND], target_readings[x])

    def test_017_read_bad_device(self):
        """ Test reading an RS485 device.
        Negative tests.
        """
        # no reg values
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/airflow/rack_1/50000006/0001')

        # non-existent board
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/airflow/rack_1/50000040/0001')

        # good board, bad device
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/airflow/rack_1/50000003/0002')

    def test_018_read_min_max_by_name(self):
        """ Test reading an RS485 device.  Read min/max values out from the second airflow sensor by name.
        """
        r = http.get(PREFIX + '/read/airflow/rack_1/50000004/cec airflow 2 - min max')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIsInstance(response[_S.AIRFLOW_MILLIMETERS_PER_SECOND], int)
        self.assertEqual(response[_S.AIRFLOW_MILLIMETERS_PER_SECOND], 399)

        r = http.get(PREFIX + '/read/airflow/rack_1/50000004/cec airflow 2 - min max')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn(_S.AIRFLOW_MILLIMETERS_PER_SECOND, response)
        self.assertIsInstance(response[_S.AIRFLOW_MILLIMETERS_PER_SECOND], int)
        self.assertEqual(response[_S.AIRFLOW_MILLIMETERS_PER_SECOND], 0)

        r = http.get(PREFIX + '/read/airflow/rack_1/50000004/cec airflow 2 - min max')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIsInstance(response[_S.AIRFLOW_MILLIMETERS_PER_SECOND], int)
        self.assertEqual(response[_S.AIRFLOW_MILLIMETERS_PER_SECOND], 399)

    def test_019_read_invalid_device_type_or_command(self):
        """ Test reading an RS485 device.  Read wrong type of device, or use wrong command.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/temperature/rack_1/50000004/cec airflow 2 - min max')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/temperature/rack_1/50000004/0001')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/power/rack_1/50000004/0001')

    def test_020_read_airflow_version(self):
        """
        Test version command on airflow sensor.
        """
        r = http.get(PREFIX + '/version/rack_1/50000004')
        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(
            'Synse RS-485 Bridge v1.0', response['firmware_version'])

    # endregion

    # region Test Fan Control
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # Test Fan Control
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def test_021_read_min_max(self):
        """ Test reading an RS485 device.  Read min/max values out from the first fan.
        """
        r = http.get(PREFIX + '/fan/rack_1/50000007/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('speed_rpm', response)
        self.assertIsInstance(response['speed_rpm'], int)
        self.assertEqual(response['speed_rpm'], 0)

        r = http.get(PREFIX + '/fan/rack_1/50000007/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('speed_rpm', response)
        self.assertIsInstance(response['speed_rpm'], int)
        self.assertEqual(response['speed_rpm'], 0xffff)

        r = http.get(PREFIX + '/fan/rack_1/50000007/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('speed_rpm', response)
        self.assertIsInstance(response['speed_rpm'], int)
        self.assertEqual(response['speed_rpm'], 0)

    def test_022_set_speed(self):
        """ Test reading/writing an RS485 device.  Set speed and read it back multiple times.
        """
        # verify starting value
        r = http.get(PREFIX + '/fan/rack_1/50000008/0001')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('speed_rpm', response)
        self.assertIsInstance(response['speed_rpm'], int)
        self.assertEqual(response['speed_rpm'], 0x7ac0)

        for x in range(0, 10):
            # set to a handful of values
            r = http.get(PREFIX + '/fan/rack_1/50000008/0001/{}'.format(str(x*100)))
            self.assertTrue(http.request_ok(r.status_code))

            response = r.json()
            self.assertIsInstance(response, dict)
            self.assertIn('speed_rpm', response)
            self.assertIsInstance(response['speed_rpm'], int)
            self.assertEqual(response['speed_rpm'], x*100)

    def test_023_read_bad_device(self):
        """ Test reading an RS485 device.  This device has no register values behind it, so should raise 500.
        """
        # no reg values
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/50000009/0001')

        # non-existent board
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/50000040/0001')

        # good board, bad device
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/50000008/0002')

    def test_024_read_min_max_by_name(self):
        """ Test reading an RS485 device.  Read min/max values out from the chamber fan by name.
        """
        r = http.get(PREFIX + '/fan/rack_1/50000007/chamber fan')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('speed_rpm', response)
        self.assertIsInstance(response['speed_rpm'], int)
        self.assertEqual(response['speed_rpm'], 0xffff)

        r = http.get(PREFIX + '/fan/rack_1/50000007/chamber fan')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('speed_rpm', response)
        self.assertIsInstance(response['speed_rpm'], int)
        self.assertEqual(response['speed_rpm'], 0)

        r = http.get(PREFIX + '/fan/rack_1/50000007/chamber fan')
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertIn('speed_rpm', response)
        self.assertIsInstance(response['speed_rpm'], int)
        self.assertEqual(response['speed_rpm'], 0xffff)

    def test_025_read_invalid_device_type_or_command(self):
        """ Test reading an RS485 device.  Read wrong type of device, or use wrong command.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/temperature/rack_1/50000007/chamber fan')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/read/temperature/rack_1/50000007/0001')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/power/rack_1/50000007/0001')

    def test_026_set_invalid_speed(self):
        """ Test writing an RS485 device.  Set invalid speed.
        """
        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/50000008/chamber fan - set-get/1756')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/50000008/chamber fan - set-get/-1')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/50000008/chamber fan - set-get/taco')

        with self.assertRaises(VaporHTTPError):
            http.get(PREFIX + '/fan/rack_1/50000008/chamber fan - set-get/9000')

    def test_027_read_fan_version(self):
        """
        Test version command on humidity sensor.
        """
        r = http.get(PREFIX + '/version/rack_1/50000008')
        response = r.json()
        self.assertIsInstance(response, dict)
        self.assertEqual(
            'Synse RS-485 Bridge v1.0', response['firmware_version'])

    # endregion
