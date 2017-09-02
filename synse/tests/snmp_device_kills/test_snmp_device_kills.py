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
import json
import logging

import docker

from synse.tests.synse_test import SynseHttpTest
from synse.tests.test_utils import Uri
from synse.vapor_common import http
from synse.vapor_common.errors import VaporHTTPError
from synse.vapor_common.tests.utils.strings import _S

logger = logging.getLogger(__name__)


# region Test specific string constants.

BOARD_60000000 = '60000000'
BOARD_60000001 = '60000001'
BOARD_60000002 = '60000002'
EXPECTED_VAPOR_HTTP_ERROR = 'Should have raised VaporHTTPError.'
NO_VERIFICATION_FOR_BOARD = 'No verification method for board_id {}'
RACK_1 = 'rack_1'
RACK_2 = 'rack_2'
SNMP_EMULATOR_SYNSE_TESTDEVICE1_BOARD1 = 'snmp-emulator-synse-testdevice1-board1'
SNMP_EMULATOR_SYNSE_TESTDEVICE1_BOARD2 = 'snmp-emulator-synse-testdevice1-board2'

# endregion


class SnmpDeviceKillsTestCase(SynseHttpTest):
    """ This test brings up two SNMP emulators for TestDevice1. The goal here
    is to allow the Synse container to initialize successfully with all
    emulators running. Before these tests start we docker kill one of the
    TestDevice1 emulators. The goal here is to find out what happens when
    SNMP servers fall over after Synse initialization. No forced scan is
    done here so Synse will still attempt to route commands to the emulators
    that have been killed.
    """

    @classmethod
    def setUpClass(cls):
        """Verify which emulators are up and down when the test cases start."""
        logger.debug('Starting SnmpDeviceKillsTestCase.')
        logger.debug('Verify containers are either alive or killed.')

        cli = docker.Client(base_url='unix://var/run/docker.sock')

        # Kill one of the containers.
        cli.kill(SNMP_EMULATOR_SYNSE_TESTDEVICE1_BOARD1)

        # now, we get the running containers to verify
        running = cli.containers(filters={'status': 'running'})

        alive = []
        for ctr in running:
            if 'Labels' in ctr:
                for k, v in ctr['Labels'].iteritems():
                    if k == 'com.docker.compose.service':
                        alive.append(v)

        # verify that the board we expect to be running is running, and the
        # one we expect to be down is not running.
        assert SNMP_EMULATOR_SYNSE_TESTDEVICE1_BOARD1 not in alive, 'Container alive, but should be dead.'
        assert SNMP_EMULATOR_SYNSE_TESTDEVICE1_BOARD2 in alive, 'Container dead, but should be alive.'

    # region Scan Helpers

    def _verify_board_60000000(self, board):

        self._verify_common_board_fields(board)

        # Verify devices. 9 fans, 8 LEDs, 8 power.
        devices = board[_S.DEVICES]
        self.assertEqual(25, len(devices))

        # Verify fans
        self._verify_device(devices[0], '0000', _S.DEVICE_TYPE_FAN_SPEED, _S.DEVICE_TYPE_FAN_SPEED)
        self._verify_device(devices[1], '0001', _S.DEVICE_TYPE_FAN_SPEED, _S.DEVICE_TYPE_FAN_SPEED)
        self._verify_device(devices[2], '0002', _S.DEVICE_TYPE_FAN_SPEED, _S.DEVICE_TYPE_FAN_SPEED)
        self._verify_device(devices[3], '0003', _S.DEVICE_TYPE_FAN_SPEED, _S.DEVICE_TYPE_FAN_SPEED)
        self._verify_device(devices[4], '0004', _S.DEVICE_TYPE_FAN_SPEED, _S.DEVICE_TYPE_FAN_SPEED)
        self._verify_device(devices[5], '0005', _S.DEVICE_TYPE_FAN_SPEED, _S.DEVICE_TYPE_FAN_SPEED)
        self._verify_device(devices[6], '0006', _S.DEVICE_TYPE_FAN_SPEED, _S.DEVICE_TYPE_FAN_SPEED)
        self._verify_device(devices[7], '0007', _S.DEVICE_TYPE_FAN_SPEED, _S.DEVICE_TYPE_FAN_SPEED)
        self._verify_device(devices[8], '0008', _S.DEVICE_TYPE_FAN_SPEED, _S.DEVICE_TYPE_FAN_SPEED)

        # Verify LEDs
        self._verify_device(devices[9], '0009', _S.DEVICE_TYPE_LED, _S.DEVICE_TYPE_LED)
        self._verify_device(devices[10], '000a', _S.DEVICE_TYPE_LED, _S.DEVICE_TYPE_LED)
        self._verify_device(devices[11], '000b', _S.DEVICE_TYPE_LED, _S.DEVICE_TYPE_LED)
        self._verify_device(devices[12], '000c', _S.DEVICE_TYPE_LED, _S.DEVICE_TYPE_LED)
        self._verify_device(devices[13], '000d', _S.DEVICE_TYPE_LED, _S.DEVICE_TYPE_LED)
        self._verify_device(devices[14], '000e', _S.DEVICE_TYPE_LED, _S.DEVICE_TYPE_LED)
        self._verify_device(devices[15], '000f', _S.DEVICE_TYPE_LED, _S.DEVICE_TYPE_LED)
        self._verify_device(devices[16], '0010', _S.DEVICE_TYPE_LED, _S.DEVICE_TYPE_LED)

        # Verify power (outlets)
        self._verify_device(devices[17], '0011', _S.DEVICE_TYPE_POWER, _S.DEVICE_TYPE_POWER)
        self._verify_device(devices[18], '0012', _S.DEVICE_TYPE_POWER, _S.DEVICE_TYPE_POWER)
        self._verify_device(devices[19], '0013', _S.DEVICE_TYPE_POWER, _S.DEVICE_TYPE_POWER)
        self._verify_device(devices[20], '0014', _S.DEVICE_TYPE_POWER, _S.DEVICE_TYPE_POWER)
        self._verify_device(devices[21], '0015', _S.DEVICE_TYPE_POWER, _S.DEVICE_TYPE_POWER)
        self._verify_device(devices[22], '0016', _S.DEVICE_TYPE_POWER, _S.DEVICE_TYPE_POWER)
        self._verify_device(devices[23], '0017', _S.DEVICE_TYPE_POWER, _S.DEVICE_TYPE_POWER)
        self._verify_device(devices[24], '0018', _S.DEVICE_TYPE_POWER, _S.DEVICE_TYPE_POWER)

    def _verify_board_60000001(self, board):

        self._verify_common_board_fields(board)

        # Verify devices. 8 fans, 7 LEDs, 9 power.
        devices = board[_S.DEVICES]
        self.assertEqual(24, len(devices))

        # Verify fans
        self._verify_device(devices[0], '0000', _S.DEVICE_TYPE_FAN_SPEED, _S.DEVICE_TYPE_FAN_SPEED)
        self._verify_device(devices[1], '0001', _S.DEVICE_TYPE_FAN_SPEED, _S.DEVICE_TYPE_FAN_SPEED)
        self._verify_device(devices[2], '0002', _S.DEVICE_TYPE_FAN_SPEED, _S.DEVICE_TYPE_FAN_SPEED)
        self._verify_device(devices[3], '0003', _S.DEVICE_TYPE_FAN_SPEED, _S.DEVICE_TYPE_FAN_SPEED)
        self._verify_device(devices[4], '0004', _S.DEVICE_TYPE_FAN_SPEED, _S.DEVICE_TYPE_FAN_SPEED)
        self._verify_device(devices[5], '0005', _S.DEVICE_TYPE_FAN_SPEED, _S.DEVICE_TYPE_FAN_SPEED)
        self._verify_device(devices[6], '0006', _S.DEVICE_TYPE_FAN_SPEED, _S.DEVICE_TYPE_FAN_SPEED)
        self._verify_device(devices[7], '0007', _S.DEVICE_TYPE_FAN_SPEED, _S.DEVICE_TYPE_FAN_SPEED)

        # Verify LEDs
        self._verify_device(devices[8], '0008', _S.DEVICE_TYPE_LED, _S.DEVICE_TYPE_LED)
        self._verify_device(devices[9], '0009', _S.DEVICE_TYPE_LED, _S.DEVICE_TYPE_LED)
        self._verify_device(devices[10], '000a', _S.DEVICE_TYPE_LED, _S.DEVICE_TYPE_LED)
        self._verify_device(devices[11], '000b', _S.DEVICE_TYPE_LED, _S.DEVICE_TYPE_LED)
        self._verify_device(devices[12], '000c', _S.DEVICE_TYPE_LED, _S.DEVICE_TYPE_LED)
        self._verify_device(devices[13], '000d', _S.DEVICE_TYPE_LED, _S.DEVICE_TYPE_LED)
        self._verify_device(devices[14], '000e', _S.DEVICE_TYPE_LED, _S.DEVICE_TYPE_LED)

        # Verify power (outlets)
        self._verify_device(devices[15], '000f', _S.DEVICE_TYPE_POWER, _S.DEVICE_TYPE_POWER)
        self._verify_device(devices[16], '0010', _S.DEVICE_TYPE_POWER, _S.DEVICE_TYPE_POWER)
        self._verify_device(devices[17], '0011', _S.DEVICE_TYPE_POWER, _S.DEVICE_TYPE_POWER)
        self._verify_device(devices[18], '0012', _S.DEVICE_TYPE_POWER, _S.DEVICE_TYPE_POWER)
        self._verify_device(devices[19], '0013', _S.DEVICE_TYPE_POWER, _S.DEVICE_TYPE_POWER)
        self._verify_device(devices[20], '0014', _S.DEVICE_TYPE_POWER, _S.DEVICE_TYPE_POWER)
        self._verify_device(devices[21], '0015', _S.DEVICE_TYPE_POWER, _S.DEVICE_TYPE_POWER)
        self._verify_device(devices[22], '0016', _S.DEVICE_TYPE_POWER, _S.DEVICE_TYPE_POWER)
        self._verify_device(devices[23], '0017', _S.DEVICE_TYPE_POWER, _S.DEVICE_TYPE_POWER)

    def _verify_rack1_scan(self, response):
        """
        Common area to validate valid scan all results.
        :param response: The valid scan all response to verify.
        """
        # Get the rack.
        rack = self._get_rack_by_id(response, RACK_1)
        self._verify_common_rack_fields(rack)

        # Verify rack_id.
        self.assertEquals(RACK_1, rack[_S.RACK_ID])

        # Verify hostnames.
        hostnames = rack[_S.HOSTNAMES]
        self.assertEquals(1, len(hostnames))
        self.assertIn(SNMP_EMULATOR_SYNSE_TESTDEVICE1_BOARD1, hostnames)

        # Verify ip_addresses.
        ip_addresses = rack[_S.IP_ADDRESSES]
        self.assertEquals(1, len(ip_addresses))
        self.assertIn(SNMP_EMULATOR_SYNSE_TESTDEVICE1_BOARD1, ip_addresses)

        # Verify boards.
        boards = rack[_S.BOARDS]
        self.assertEqual(1, len(boards))

        for board in boards:
            self.assertIn(_S.BOARD_ID, board)
            board_id = board[_S.BOARD_ID]
            self.assertIsInstance(board_id, basestring)

            if board_id == BOARD_60000000:
                self._verify_board_60000000(board)
            else:
                self.fail(NO_VERIFICATION_FOR_BOARD.format(board_id))

    def _verify_rack2_scan(self, response):
        """
        Common area to validate valid scan all results.
        :param response: The valid scan all response to verify.
        """
        # Get the rack.
        rack = self._get_rack_by_id(response, RACK_2)
        self._verify_common_rack_fields(rack)

        # Verify rack_id.
        self.assertEquals(RACK_2, rack[_S.RACK_ID])

        # Verify hostnames.
        hostnames = rack[_S.HOSTNAMES]
        self.assertEquals(1, len(hostnames))
        self.assertIn(SNMP_EMULATOR_SYNSE_TESTDEVICE1_BOARD2, hostnames)

        # Verify ip_addresses.
        ip_addresses = rack[_S.IP_ADDRESSES]
        self.assertEquals(1, len(ip_addresses))
        self.assertIn(SNMP_EMULATOR_SYNSE_TESTDEVICE1_BOARD2, ip_addresses)

        # Verify boards.
        boards = rack[_S.BOARDS]
        self.assertEqual(1, len(boards))

        for board in boards:
            self.assertIn(_S.BOARD_ID, board)
            board_id = board[_S.BOARD_ID]
            self.assertIsInstance(board_id, basestring)

            if board_id == BOARD_60000001:
                self._verify_board_60000001(board)
            else:
                self.fail(NO_VERIFICATION_FOR_BOARD.format(board_id))

    def _verify_valid_scan_all(self, response, expected_rack_count):
        """
        Common area to validate valid scan all results.
        :param response: The valid scan all response to verify.
        """
        self._verify_expected_rack_count(response, expected_rack_count)
        self._verify_rack1_scan(response)
        self._verify_rack2_scan(response)

    # endregion

    # region Scan Tests

    # region Scan All

    # Scan all force is deliberately missing here. It's in SnmpDeviceKillsForceScanTestCase.

    def test_scan_all(self):
        """ Test scan all expecting happy results.
        """
        r = http.get(Uri.create(_S.URI_SCAN))
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))

        self._verify_valid_scan_all(response, 2)

    # endregion

    # region Scan

    def test_scan_by_rack1(self):
        """ Test scan rack_1 expecting happy results.
        """
        r = http.get(Uri.create(_S.URI_SCAN, RACK_1))
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))

        self._verify_expected_rack_count(response, 1)
        self._verify_rack1_scan(response)

    def test_scan_by_rack2(self):
        """ Test scan rack_2 expecting happy results.
        """
        r = http.get(Uri.create(_S.URI_SCAN, RACK_2))
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))

        self._verify_expected_rack_count(response, 1)
        self._verify_rack2_scan(response)

    def test_scan_by_rack_does_not_exist(self):
        """ Test scan rack_965 that does not exist.
        """
        try:
            http.get(Uri.create(_S.URI_SCAN, 'rack_965'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_NO_RACK_FOUND_WITH_ID.format('rack_965'))

    def test_scan_by_rack_and_board(self):
        """ Test scan rack_1, board 60000000 expecting happy results.
        """
        r = http.get(Uri.create(_S.URI_SCAN, RACK_1, BOARD_60000000))
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))

        self._verify_expected_rack_count(response, 1)
        self._verify_rack1_scan(response)

    def test_scan_by_rack_and_board_where_board_does_not_exist(self):
        """ Test scan rack_1, board 60010000 expecting sadness.
        """
        try:
            http.get(Uri.create(_S.URI_SCAN, RACK_1, '60010000'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_NO_REGISTERED_DEVICE_FOR_BOARD.format(int('60010000', 16)))

    # endregion

    # endregion

    # endregion

    # region Version

    def test_version_rack1(self):
        """SNMP version testing. Happy case."""
        response = http.get(Uri.create(_S.URI_VERSION, RACK_1, BOARD_60000000)).json()
        self._verify_version_snmp(response, _S.SNMP_V2C)

    def test_version_board_does_not_exist_rack1(self):
        """SNMP version testing. Board does not exist. Sad case."""
        try:
            http.get(Uri.create(_S.URI_VERSION, RACK_1, BOARD_60000002))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(
                e, 500, _S.ERROR_NO_REGISTERED_DEVICE_FOR_BOARD.format(int(BOARD_60000002, 16)))

    def test_version_rack2(self):
        """SNMP version testing. Happy case."""
        response = http.get(Uri.create(_S.URI_VERSION, RACK_2, BOARD_60000001)).json()
        self._verify_version_snmp(response, _S.SNMP_V2C)

    def test_version_board_does_not_exist_rack2(self):
        """SNMP version testing. Board does not exist. Sad case."""
        try:
            http.get(Uri.create(_S.URI_VERSION, RACK_2, BOARD_60000002))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(
                e, 500, _S.ERROR_NO_REGISTERED_DEVICE_FOR_BOARD.format(int(BOARD_60000002, 16)))

    # endregion

    # region Read

    def test_read_temperature_rack1(self):
        """SNMP read of temperature variable. Sad case. Emulator is dead."""
        logger.debug('test_read_temperature')
        try:
            http.get(
                Uri.read_temperature(RACK_1, BOARD_60000000, '0001'), timeout=7)
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.SNMP_EMULATOR_DOWN)

    def test_read_voltage_rack1(self):
        """SNMP read of voltage variable. Sad case. Emulator is dead."""
        logger.debug('test_read_voltage')
        try:
            http.get(Uri.read_voltage(RACK_1, BOARD_60000000, '0004'), timeout=7)
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.SNMP_EMULATOR_DOWN)

    def test_read_fan_speed_rack1(self):
        """SNMP read of fan speed (rpm_ variable). Sad case. Emulator is dead."""
        logger.debug('test_read_fan_speed_rack1')
        try:
            http.get(Uri.read_fan_speed(RACK_1, BOARD_60000000, '0005'), timeout=7)
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.SNMP_EMULATOR_DOWN)

    # NOTE: Power supply read is NYI. Need the use case to implement this.
    # PDUs and smart power strips can just be power until we get a customer ask
    # for power supply.

    def test_read_board_does_not_exist_rack1(self):
        """Test read where board does not exist. Sad case."""
        try:
            http.get(Uri.read_temperature(RACK_1, '60000006', '0001'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_NO_REGISTERED_DEVICE_FOR_BOARD.format(int('60000006', 16)))

    def test_read_device_does_not_exist_rack1(self):
        """Test read where device does not exist. Sad case."""
        try:
            http.get(Uri.read_temperature(RACK_1, BOARD_60000000, 'F001'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_NO_DEVICE_WITH_ID.format('f001'))

    def test_read_device_not_yet_supported_rack1(self):
        """Test read device not yet supported. Board and device are there, we just
        don't support humidity sensors yet. Sad case. Emulator is dead."""
        try:
            http.get(Uri.read_humidity(RACK_1, BOARD_60000000, '0003'), timeout=7)
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.SNMP_EMULATOR_DOWN)

    def test_read_wrong_device_type_in_url_rack1(self):
        """Read a valid device, but wrong type in the url. Read voltage, but
        it's a temperature sensor. Sad case. Emulator is down."""
        try:
            http.get(Uri.read_voltage(RACK_1, BOARD_60000000, '0001'), timeout=7)
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.SNMP_EMULATOR_DOWN)

    def test_read_fan_speed_rack1_board0(self):
        """SNMP read of fan speed. Sad case. Emulator is dead."""
        logger.debug('test_read_fan_speed_rack1_board0')
        try:
            http.get(Uri.read_fan_speed(RACK_1, BOARD_60000000, '0005'), timeout=7)
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.SNMP_EMULATOR_DOWN)

    def test_read_fan_speed_rack2_board1(self):
        """SNMP read of fan speed. Happy case."""
        logger.debug('test_read_fan_speed_rack2_board1')
        response = http.get(Uri.read_fan_speed(RACK_2, BOARD_60000001, '0005')).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_read_fan_response(response, _S.OK, [], 5)

    def test_read_voltage_rack1_board0(self):
        """SNMP read of voltage variable. Sad case. Emulator is dead."""
        logger.debug('test_read_voltage_rack1_board0')
        try:
            http.get(Uri.read_voltage(RACK_1, BOARD_60000000, '0014'), timeout=7)
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.SNMP_EMULATOR_DOWN)

    def test_read_voltage_rack2_board1(self):
        """SNMP read of voltage variable. Happy case."""
        logger.debug('test_read_voltage_rack2_board1')
        response = http.get(Uri.read_voltage(RACK_2, BOARD_60000001, '0014'), timeout=7).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_read_voltage_response(response, _S.OK, [], 14)

    # endregion

    # Some odd code folding issue here does not like it when the test below is in region Read

    # region Read2

    def test_read_fan_speed_rack1_board0_down(self):
        """SNMP read of fan speed. Sad case. Emulator is down."""
        logger.debug('test_read_fan_speed_rack1_board0')
        try:
            http.get(Uri.read_fan_speed(RACK_1, BOARD_60000000, '0000'), timeout=7)
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.SNMP_EMULATOR_DOWN)

    # endregion

    # region Fan

    def test_read_write_fan_speed_rack1_board0(self):
        """SNMP read of fan speed. Sad case. Emulator is down."""
        logger.debug('test_read_write_fan_speed_rack1_board0')
        base_uri = Uri.create(_S.URI_FAN, RACK_1, BOARD_60000000, '0004')
        try:
            http.get(base_uri, timeout=7)
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.SNMP_EMULATOR_DOWN)

    def test_read_write_fan_speed_rack2_board1(self):
        """SNMP read of fan speed. Happy case. Read, write, set back to the original.
        This is a lot like test_read_write_fan_speed_rack1_board0, but verifies that
        command routing is going to the correct emulator.
        NOTE: If a write fails or the write back to original fails, this test may be
        non-reentrant. To avoid reentrancy issues, no other tests should run against
        this device at /rack_2/60000001/0004.
        """
        logger.debug('test_read_write_fan_speed_rack2_board1')
        base_uri = Uri.create(_S.URI_FAN, RACK_2, BOARD_60000001, '0004')
        response = http.get(base_uri).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_read_fan_response(response, _S.OK, [], 21)

        response = http.get(Uri.append(base_uri, '300')).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_read_fan_response(response, _S.OK, [], 300)

        logger.debug('second read')
        response = http.get(base_uri).json()
        self._verify_read_fan_response(response, _S.OK, [], 300)

        logger.debug('second write (to initial)')
        response = http.get(Uri.append(base_uri, '21')).json()
        self._verify_read_fan_response(response, _S.OK, [], 21)

        logger.debug('third read')
        response = http.get(base_uri).json()
        self._verify_read_fan_response(response, _S.OK, [], 21)

    def test_write_fan_speed_rack1_board0_wrong_device_type(self):
        """SNMP write of fan speed. Sad case. Fan control on LED."""
        logger.debug('test_write_fan_speed_rack1_board0_wrong_device_type')
        try:
            http.get(Uri.create(_S.URI_FAN, RACK_1, BOARD_60000000, '000c', '300'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_FAN_COMMAND_NOT_SUPPORTED)

    def test_write_fan_speed_rack1_board0_device_does_not_exist(self):
        """SNMP read of fan speed. Sad case. Fan control on non-existent device."""
        logger.debug('test_write_fan_speed_rack1_board0_wrong_device_type')
        try:
            http.get(Uri.create(_S.URI_FAN, RACK_1, BOARD_60000000, 'f001', '300'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_NO_DEVICE_WITH_ID.format('f001'))

    # endregion

    # region Power Reads

    def test_power_read_rack1(self):
        logger.debug('test_power_read_rack1 (emulator was killed)')
        base_uri = Uri.create(_S.URI_POWER, RACK_1, BOARD_60000000, '0002')
        try:
            http.get(base_uri, timeout=7)
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_POWER_COMMAND_NOT_SUPPORTED)

    def test_power_wrong_device_type_rack1(self):
        """Power read a valid device, but wrong device type.
        Read power, but it's a temperature sensor. Sad case.
        Emulator is dead."""
        try:
            http.get(Uri.create(_S.URI_POWER, RACK_1, BOARD_60000000, '0001'), timeout=7)
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_POWER_COMMAND_NOT_SUPPORTED)

    def test_power_board_does_not_exist_rack2(self):
        """Test power where board does not exist. Sad case."""
        try:
            http.get(Uri.create(_S.URI_POWER, RACK_2, '60000006', '0002'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_NO_REGISTERED_DEVICE_FOR_BOARD.format(int('60000006', 16)))

    def test_power_device_does_not_exist_rack2(self):
        """Test power where device does not exist. Sad case."""
        try:
            http.get(Uri.create(_S.URI_POWER, RACK_2, BOARD_60000001, 'F001'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_NO_DEVICE_WITH_ID.format('f001'))

    def test_power_write_rack1(self):
        """Test power write where the underlying device does not support it.
        Sad case. Emulator is down."""
        try:
            http.get(Uri.create(_S.URI_POWER, RACK_1, BOARD_60000000, '0002', _S.ON), timeout=7)
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_POWER_COMMAND_NOT_SUPPORTED)

    def test_power_read_rack1_bad(self):
        """Sad case power read on the first rack. Emulator is dead."""
        logger.debug('test_power_read_rack1')
        try:
            http.get(Uri.create(_S.URI_POWER, RACK_1, BOARD_60000000, '0011'), timeout=7)
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.SNMP_EMULATOR_DOWN)

    def test_power_read_rack2_not_supported(self):
        """Sad case power read on the second rack. Power command on a fan."""
        try:
            http.get(Uri.create(_S.URI_POWER, RACK_2, BOARD_60000001, '0002'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_POWER_COMMAND_NOT_SUPPORTED)

    # endregion

    # region Power Writes

    def test_read_write_power_rack1_board0(self):
        """SNMP read/write of power. Sad case. Emulator is down.
        """
        logger.debug('test_read_write_power_rack1_board0')
        base_uri = Uri.create(_S.URI_POWER, RACK_1, BOARD_60000000, '0012')
        try:
            http.get(base_uri, timeout=7)
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.SNMP_EMULATOR_DOWN)

    def test_read_write_power_rack2_board1(self):
        """SNMP read/write of power. Happy case. Simulates an SNMP PDU.
        Read, off, read, on, read, cycle, read, off, read.
        This is a lot like test_read_write_power_rack1_board0, but verifies that
        command routing is going to the correct emulator.
        NOTE: If a write fails or the write back to original fails, this test may be
        non-reentrant. To avoid reentrancy issues, no other tests should run against
        this device at /rack_2/60000001/0012.
        """
        logger.debug('test_read_write_power_rack2_board1')
        base_uri = Uri.create(_S.URI_POWER, RACK_2, BOARD_60000001, '0012')
        response = http.get(base_uri).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_power_response(response, 26, False, True, _S.ON)

        logger.debug('set power off')
        response = http.get(Uri.append(base_uri, _S.OFF)).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_power_response(response, 26, False, True, _S.OFF)

        logger.debug('second read')
        response = http.get(base_uri).json()
        self._verify_power_response(response, 26, False, True, _S.OFF)

        logger.debug('set power on')
        response = http.get(Uri.append(base_uri, _S.ON)).json()
        self._verify_power_response(response, 26, False, True, _S.ON)

        logger.debug('third read')
        response = http.get(base_uri).json()
        self._verify_power_response(response, 26, False, True, _S.ON)

        logger.debug('set power cycle')
        response = http.get(Uri.append(base_uri, _S.CYCLE)).json()
        self._verify_power_response(response, 26, False, True, _S.ON)

        logger.debug('fourth read')
        response = http.get(base_uri).json()
        self._verify_power_response(response, 26, False, True, _S.ON)

        logger.debug('set power off')
        response = http.get(Uri.append(base_uri, _S.OFF)).json()
        self._verify_power_response(response, 26, False, True, _S.OFF)

        logger.debug('fifth read')
        response = http.get(base_uri).json()
        self._verify_power_response(response, 26, False, True, _S.OFF)

    def test_write_power_rack1_board0_wrong_device_type(self):
        """SNMP read of power. Sad case. Power command on LED."""
        try:
            http.get(Uri.create(_S.URI_POWER, RACK_1, BOARD_60000000, '000c', '300'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(
                e, 500, _S.ERROR_POWER_COMMAND_NOT_SUPPORTED)

    def test_write_power_rack2_board0_device_does_not_exist(self):
        """SNMP read of power. Sad case. Power command on non-existent device."""
        logger.debug('test_write_fan_speed_rack2_board0_wrong_device_type')
        try:
            http.get(Uri.create(_S.URI_POWER, RACK_1, BOARD_60000000, 'f001', '300'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_NO_DEVICE_WITH_ID.format('f001'))

    # endregion

    # region LED Writes

    def test_read_write_led_rack2_board0(self):
        """SNMP read/write of LED. Sad case. Emulator is down."""
        logger.debug('test_read_write_led_rack2_board0')
        base_uri = Uri.create(_S.URI_LED, RACK_1, BOARD_60000000, '000d')
        try:
            http.get(base_uri, timeout=7)
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.SNMP_EMULATOR_DOWN)

    def test_read_write_led_rack2_board1(self):
        """SNMP read/write of LED. Happy case.
        Read, off, read, on, read, cycle, read, off, read.
        This is a lot like test_read_write_led_rack1_board0, but verifies that
        command routing is going to the correct emulator. (Initial read is different.)
        NOTE: If a write fails or the write back to original fails, this test may be
        non-reentrant. To avoid reentrancy issues, no other tests should run against
        this device at /rack_1/60000000/000d.
        """
        logger.debug('test_read_write_led_rack2_board1')
        base_uri = Uri.create(_S.URI_LED, RACK_2, BOARD_60000001, '000d')
        response = http.get(base_uri).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_led_response(response, _S.ON, 'ffffff', _S.BLINK_ON)

        logger.debug('set led off')
        response = http.get(Uri.append(base_uri, _S.OFF)).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_led_response(response, _S.OFF, 'ffffff', _S.BLINK_ON)

        logger.debug('second read')
        response = http.get(base_uri).json()
        self._verify_led_response(response, _S.OFF, 'ffffff', _S.BLINK_ON)

        logger.debug('set led on')
        response = http.get(Uri.append(base_uri, _S.ON)).json()
        self._verify_led_response(response, _S.ON, 'ffffff', _S.BLINK_ON)

        logger.debug('third read')
        response = http.get(base_uri).json()
        self._verify_led_response(response, _S.ON, 'ffffff', _S.BLINK_ON)

        logger.debug('set led on, color blue, blink on')
        response = http.get(Uri.append(base_uri, _S.ON, 'FF', _S.BLINK_ON)).json()
        self._verify_led_response(response, _S.ON, '0000ff', _S.BLINK_ON)

        logger.debug('fourth read')
        response = http.get(base_uri).json()
        self._verify_led_response(response, _S.ON, '0000ff', _S.BLINK_ON)

        logger.debug('set led on, color different, blink off')
        response = http.get(Uri.append(base_uri, _S.ON, 'f0f0f0', _S.BLINK_OFF)).json()
        self._verify_led_response(response, _S.ON, 'f0f0f0', _S.BLINK_OFF)

        logger.debug('fifth read')
        response = http.get(base_uri).json()
        self._verify_led_response(response, _S.ON, 'f0f0f0', _S.BLINK_OFF)

        logger.debug('set led on, color as above, blink on')
        response = http.get(Uri.append(base_uri, _S.ON, 'f0f0f0', _S.BLINK_ON)).json()
        self._verify_led_response(response, _S.ON, 'f0f0f0', _S.BLINK_ON)

        logger.debug('sixth read')
        response = http.get(base_uri).json()
        self._verify_led_response(response, _S.ON, 'f0f0f0', _S.BLINK_ON)

        logger.debug('set led on, color back to original, blink on')
        response = http.get(Uri.append(base_uri, _S.ON, 'ffffff', _S.BLINK_ON)).json()
        self._verify_led_response(response, _S.ON, 'ffffff', _S.BLINK_ON)

        logger.debug('seventh read')
        response = http.get(base_uri).json()
        self._verify_led_response(response, _S.ON, 'ffffff', _S.BLINK_ON)

    # endregion

    def test_write_led_rack1_board0_wrong_device_type(self):
        """SNMP write of LED Sad case. LED command on LED."""
        try:
            http.get(Uri.create(_S.URI_LED, RACK_1, BOARD_60000000, '0016', _S.ON))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(
                e, 500, _S.ERROR_LED_COMMAND_NOT_SUPPORTED)

    def test_write_led_rack1_board0_device_does_not_exist(self):
        """SNMP read of fan speed. Sad case. Fan control on non-existent device."""
        logger.debug('test_write_led_rack1_board0_device_does_not_exist')
        try:
            http.get(Uri.create(_S.URI_LED, RACK_1, BOARD_60000000, 'f071', _S.ON))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_NO_DEVICE_WITH_ID.format('f071'))

    def test_led_set_color_without_blink_rack2_board1(self):
        """SNMP read/write of LED. Sad case.
        NOTE: If a write fails or the write back to original fails, this test may be
        non-reentrant.
        """
        # Make sure the device is there.
        logger.debug('test_led_set_color_without_blink_rack2_board1')
        base_uri = Uri.create(_S.URI_LED, RACK_2, BOARD_60000001, '000c')
        response = http.get(base_uri).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_led_response(response, _S.ON, 'ff0000', _S.BLINK_OFF)

        logger.debug('set color without blink')
        try:
            http.get(Uri.append(base_uri, _S.ON, '0000FF'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            # You'll get a 404 here because the blueprint does not exist.
            self._verify_vapor_http_error(e, 404, _S.ERROR_FLASK_404)

    def test_led_set_invalid_states_rack2_board1(self):
        """SNMP write of LED. Sad case.
        NOTE: If a write fails or the write back to original fails, this test may be
        non-reentrant.
        """
        # Make sure the device is there.
        logger.debug('test_led_set_color_without_blink_rack2_board1')
        base_uri = Uri.create(_S.URI_LED, RACK_2, BOARD_60000001, '000c')
        response = http.get(base_uri).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_led_response(response, _S.ON, 'ff0000', _S.BLINK_OFF)

        logger.debug('set onn')
        try:
            http.get(Uri.append(base_uri, 'onn'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            # You'll get a 404 here because the blueprint does not exist.
            self._verify_vapor_http_error(e, 500, _S.ERROR_INVALID_STATE_LED)

        logger.debug('set color out of range')
        try:
            http.get(Uri.append(base_uri, _S.ON, '1000000', _S.BLINK_OFF))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            # You'll get a 404 here because the blueprint does not exist.
            self._verify_vapor_http_error(e, 500, _S.ERROR_INVALID_COLOR_LED)

        logger.debug('set invalid blink')
        try:
            http.get(Uri.append(base_uri, _S.ON, '000000', 'blank'))
            self.fail('Should have raised VaporHTTPError.')
        except VaporHTTPError as e:
            # You'll get a 404 here because the blueprint does not exist.
            self._verify_vapor_http_error(e, 500, _S.ERROR_INVALID_BLINK_LED)

        logger.debug('empty check')
        try:
            http.get(Uri.append(base_uri, '', '', ''))
            self.fail('Should have raised VaporHTTPError.')
        except VaporHTTPError as e:
            # You'll get a 404 here because the blueprint does not exist.
            self._verify_vapor_http_error(e, 404, _S.ERROR_FLASK_404)

        logger.debug('empty check two')
        try:
            http.get(Uri.append(base_uri, '', 'F', _S.BLINK_OFF))
            self.fail('Should have raised VaporHTTPError.')
        except VaporHTTPError as e:
            # You'll get a 404 here because the blueprint does not exist.
            self._verify_vapor_http_error(e, 404, _S.ERROR_FLASK_404)
