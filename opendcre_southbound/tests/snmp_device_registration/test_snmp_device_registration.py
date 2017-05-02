#!/usr/bin/env python
""" OpenDCRE Southbound SNMP Device Registration Tests

    \\//
     \/apor IO
"""
import json
import logging

from opendcre_southbound.tests.opendcre_test import OpenDcreHttpTest
from opendcre_southbound.tests.test_utils import Uri
from vapor_common import http
from vapor_common.errors import VaporHTTPError
from vapor_common.tests.utils.strings import _S

logger = logging.getLogger(__name__)

# region Test specific string constants.

BOARD_60000000 = '60000000'
BOARD_60000001 = '60000001'
BOARD_60000002 = '60000002'
EXPECTED_VAPOR_HTTP_ERROR = 'Should have raised VaporHTTPError.'
NO_VERIFICATION_FOR_BOARD = 'No verification method for board_id {}'
RACK_1 = 'rack_1'
RACK_2 = 'rack_2'
SNMP_EMULATOR_OPENDCRE_TESTDEVICE1_BOARD1 = 'snmp-emulator-opendcre-testdevice1-board1'
SNMP_EMULATOR_OPENDCRE_TESTDEVICE1_BOARD2 = 'snmp-emulator-opendcre-testdevice1-board2'

# endregion


class SnmpDeviceRegistrationTestCase(OpenDcreHttpTest):

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
        self.assertIn(SNMP_EMULATOR_OPENDCRE_TESTDEVICE1_BOARD1, hostnames)

        # Verify ip_addresses.
        ip_addresses = rack[_S.IP_ADDRESSES]
        self.assertEquals(1, len(ip_addresses))
        self.assertIn(SNMP_EMULATOR_OPENDCRE_TESTDEVICE1_BOARD1, ip_addresses)

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
        self.assertIn(SNMP_EMULATOR_OPENDCRE_TESTDEVICE1_BOARD2, hostnames)

        # Verify ip_addresses.
        ip_addresses = rack[_S.IP_ADDRESSES]
        self.assertEquals(1, len(ip_addresses))
        self.assertIn(SNMP_EMULATOR_OPENDCRE_TESTDEVICE1_BOARD2, ip_addresses)

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

    def test_scan_all_force(self):
        """ Test scan all force expecting happy results.
        """
        # This can fail under memory pressure (Docker is a memory leak),
        # so upped the timeout.
        r = http.get(Uri.create(_S.URI_SCAN_FORCE), timeout=10)
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))

        # we have three racks defined in the config, but one rack contains an invalid
        # snmp server, so we do not expect to see that rack populated here.
        self._verify_valid_scan_all(response, 2)

    def test_scan_all(self):
        """ Test scan all expecting happy results.
        """
        r = http.get(Uri.create(_S.URI_SCAN))
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))

        # we have three racks defined in the config, but one rack contains an invalid
        # snmp server, so we do not expect to see that rack populated here.
        self._verify_valid_scan_all(response, 2)

    # endregion

    # region Scan

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

    # endregion

    # endregion

    # endregion

    # region Version

    def test_version_rack2(self):
        """SNMP version testing. Happy case."""
        response = http.get(Uri.create(_S.URI_VERSION, RACK_1, BOARD_60000000)).json()
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

    def test_read_fan_speed_rack2_board1(self):
        """SNMP read of fan speed. Happy case."""
        logger.debug('test_read_fan_speed_rack2_board1')
        response = http.get(Uri.read_fan_speed(RACK_2, BOARD_60000000, '0005')).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_read_fan_response(response, _S.OK, [], 25)

    def test_read_fan_speed_rack2_board2(self):
        """SNMP read of fan speed. Happy case."""
        logger.debug('test_read_fan_speed_rack2_board2')
        response = http.get(Uri.read_fan_speed(RACK_2, BOARD_60000001, '0005')).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_read_fan_response(response, _S.OK, [], 5)

    def test_read_voltage_rack2_board1(self):
        """SNMP read of voltage variable. Happy case."""
        logger.debug('test_read_voltage_rack2_board1')
        response = http.get(Uri.read_voltage(RACK_2, BOARD_60000000, '0014')).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_read_voltage_response(response, _S.OK, [], 29)

    def test_read_voltage_rack2_board2(self):
        """SNMP read of voltage variable. Happy case."""
        logger.debug('test_read_voltage_rack2_board1')
        response = http.get(Uri.read_voltage(RACK_2, BOARD_60000001, '0014')).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_read_voltage_response(response, _S.OK, [], 14)

    # endregion

    # Some odd code folding issue here does not like it when the test below is in region Read

    # region Read2

    def test_read_fan_speed_rack2(self):
        """SNMP read of fan speed. Happy case."""
        logger.debug('test_read_fan_speed_rack2')
        response = http.get(Uri.read_fan_speed(RACK_2, BOARD_60000000, '0000')).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_read_fan_response(response, _S.OK, [], 20)

    # endregion

    # region Fan

    def test_read_write_fan_speed_rack2_board1(self):
        """SNMP read of fan speed. Happy case. Read, write, set back to the original.
        NOTE: If a write fails or the second write back to the original fails, this
        test may be non-reentrant. To avoid reentrancy issues, no other tests should
        run against this device at /rack_2/60000001/0004.
        """
        logger.debug('test_read_write_fan_speed_rack2_board1')
        base_uri = Uri.create(_S.URI_FAN, RACK_2, BOARD_60000000, '0004')
        response = http.get(base_uri).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_read_fan_response(response, _S.OK, [], 300)

        logger.debug('first write')
        response = http.get(Uri.append(base_uri, '500')).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_read_fan_response(response, _S.OK, [], 500)

        logger.debug('second read')
        response = http.get(base_uri).json()
        self._verify_read_fan_response(response, _S.OK, [], 500)

        logger.debug('second write (to initial)')
        response = http.get(Uri.append(base_uri, '300')).json()
        self._verify_read_fan_response(response, _S.OK, [], 300)

        logger.debug('third read')
        response = http.get(base_uri).json()
        self._verify_read_fan_response(response, _S.OK, [], 300)

    def test_read_write_fan_speed_rack2_board2(self):
        """SNMP read of fan speed. Happy case. Read, write, set back to the original.
        This is a lot like test_read_write_fan_speed_rack2_board1, but verifies that
        command routing is going to the correct emulator.
        NOTE: If a write fails or the write back to original fails, this test may be
        non-reentrant. To avoid reentrancy issues, no other tests should run against
        this device at /rack_2/60000002/0004.
        """
        logger.debug('test_read_write_fan_speed_rack2_board2')
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

    def test_write_fan_speed_rack2_board1_wrong_device_type(self):
        """SNMP write of fan speed. Sad case. Fan control on LED."""
        logger.debug('test_write_fan_speed_rack2_board1_wrong_device_type')
        try:
            http.get(Uri.create(_S.URI_FAN, RACK_2, BOARD_60000000, '000c', '300'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_FAN_COMMAND_NOT_SUPPORTED)

    def test_write_fan_speed_rack2_board1_device_does_not_exist(self):
        """SNMP read of fan speed. Sad case. Fan control on non-existent device."""
        logger.debug('test_write_fan_speed_rack2_board1_wrong_device_type')
        try:
            http.get(Uri.create(_S.URI_FAN, RACK_2, BOARD_60000000, 'f001', '300'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_NO_DEVICE_WITH_ID.format('f001'))

    # endregion

    # region Power Reads

    def test_power_read_rack2(self):
        """Happy case power read on the second rack."""
        logger.debug('test_power_read_rack2')
        response = http.get(Uri.create(_S.URI_POWER, RACK_2, BOARD_60000000, '0011')).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_power_response(response, 27, False, True, _S.OFF)

    # endregion

    # region Power Writes

    def test_read_write_power_rack2_board1(self):
        """SNMP read/write of power. Happy case. Simulates an SNMP PDU.
        Read, off, read, on, read, cycle, read, off, read.
        This is a lot like test_read_write_power_rack2_board1, but verifies that
        command routing is going to the correct emulator.
        Also here the initial power state is off.
        NOTE: If a write fails or the write back to original fails, this test may be
        non-reentrant. To avoid reentrancy issues, no other tests should run against
        this device at /rack_2/60000001/0012.
        """
        logger.debug('test_read_write_power_rack2_board1')
        base_uri = Uri.create(_S.URI_POWER, RACK_2, BOARD_60000000, '0012')
        response = http.get(base_uri).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_power_response(response, 26, False, True, _S.OFF)

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

    def test_read_write_power_rack2_board2(self):
        """SNMP read/write of power. Happy case. Simulates an SNMP PDU.
        Read, off, read, on, read, cycle, read, off, read.
        This is a lot like test_read_write_power_rack2_board1, but verifies that
        command routing is going to the correct emulator.
        NOTE: If a write fails or the write back to original fails, this test may be
        non-reentrant. To avoid reentrancy issues, no other tests should run against
        this device at /rack_2/60000002/0012.
        """
        logger.debug('test_read_write_power_rack2_board2')
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

    def test_write_power_rack2_board1_wrong_device_type(self):
        """SNMP read of power. Sad case. Power command on LED."""
        try:
            http.get(Uri.create(_S.URI_POWER, RACK_2, BOARD_60000000, '000c', '300'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(
                e, 500, _S.ERROR_POWER_COMMAND_NOT_SUPPORTED)

    def test_write_power_rack2_board1_device_does_not_exist(self):
        """SNMP read of power. Sad case. Power command on non-existent device."""
        logger.debug('test_write_fan_speed_rack2_board1_wrong_device_type')
        try:
            http.get(Uri.create(_S.URI_POWER, RACK_2, BOARD_60000000, 'f001', '300'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_NO_DEVICE_WITH_ID.format('f001'))

    # endregion

    # region LED Writes

    def test_read_write_led_rack2_board1(self):
        """SNMP read/write of LED. Happy case.
        Read, off, read, on, read, cycle, read, off, read.
        This is a lot like test_read_write_led_rack2_board1, but verifies that
        command routing is going to the correct emulator. (Initial read is different.)
        NOTE: If a write fails or the write back to original fails, this test may be
        non-reentrant. To avoid reentrancy issues, no other tests should run against
        this device at /rack_2/60000001/000d.
        """
        logger.debug('test_read_write_led_rack2_board1')
        base_uri = Uri.create(_S.URI_LED, RACK_2, BOARD_60000000, '000d')
        response = http.get(base_uri).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_led_response(response, _S.OFF, '00000f', _S.BLINK_OFF)

        logger.debug('set led off')
        response = http.get(Uri.append(base_uri, _S.OFF)).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_led_response(response, _S.OFF, '00000f', _S.BLINK_OFF)

        logger.debug('second read')
        response = http.get(base_uri).json()
        self._verify_led_response(response, _S.OFF, '00000f', _S.BLINK_OFF)

        logger.debug('set led on')
        response = http.get(Uri.append(base_uri, _S.ON)).json()
        self._verify_led_response(response, _S.ON, '00000f', _S.BLINK_OFF)

        logger.debug('third read')
        response = http.get(base_uri).json()
        self._verify_led_response(response, _S.ON, '00000f', _S.BLINK_OFF)

        logger.debug('set led on, color white, blink steady')
        response = http.get(Uri.append(base_uri, _S.ON, 'FFFFFF', _S.BLINK_OFF)).json()
        self._verify_led_response(response, _S.ON, 'ffffff', _S.BLINK_OFF)

        logger.debug('fourth read')
        response = http.get(base_uri).json()
        self._verify_led_response(response, _S.ON, 'ffffff', _S.BLINK_OFF)

        logger.debug('set led on, color red, blink on')
        response = http.get(Uri.append(base_uri, _S.ON, 'FF0000', _S.BLINK_ON)).json()
        self._verify_led_response(response, _S.ON, 'ff0000', _S.BLINK_ON)

        logger.debug('fifth read')
        response = http.get(base_uri).json()
        self._verify_led_response(response, _S.ON, 'ff0000', _S.BLINK_ON)

        logger.debug('set led on, color green, blink off')
        response = http.get(Uri.append(base_uri, _S.ON, 'FF00', _S.BLINK_OFF)).json()
        self._verify_led_response(response, _S.ON, '00ff00', _S.BLINK_OFF)

        logger.debug('sixth read')
        response = http.get(base_uri).json()
        self._verify_led_response(response, _S.ON, '00ff00', _S.BLINK_OFF)

        logger.debug('set led off, color back to original, blink off')
        response = http.get(Uri.append(base_uri, _S.OFF, 'F', _S.BLINK_OFF)).json()
        self._verify_led_response(response, _S.OFF, '00000f', _S.BLINK_OFF)

        logger.debug('seventh read')
        response = http.get(base_uri).json()
        self._verify_led_response(response, _S.OFF, '00000f', _S.BLINK_OFF)

    def test_read_write_led_rack2_board2(self):
        """SNMP read/write of LED. Happy case.
        Read, off, read, on, read, cycle, read, off, read.
        This is a lot like test_read_write_led_rack2_board1, but verifies that
        command routing is going to the correct emulator. (Initial read is different.)
        NOTE: If a write fails or the write back to original fails, this test may be
        non-reentrant. To avoid reentrancy issues, no other tests should run against
        this device at /rack_2/60000001/000d.
        """
        logger.debug('test_read_write_led_rack2_board2')
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

    def test_write_led_rack2_board1_wrong_device_type(self):
        """SNMP write of LED Sad case. LED command on LED."""
        try:
            http.get(Uri.create(_S.URI_LED, RACK_2, BOARD_60000000, '0016', _S.ON))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(
                e, 500, _S.ERROR_LED_COMMAND_NOT_SUPPORTED)

    def test_write_led_rack2_board1_device_does_not_exist(self):
        """SNMP read of fan speed. Sad case. Fan control on non-existent device."""
        logger.debug('test_write_led_rack2_board1_device_does_not_exist')
        try:
            http.get(Uri.create(_S.URI_LED, RACK_2, BOARD_60000000, 'f071', _S.ON))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)
        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_NO_DEVICE_WITH_ID.format('f071'))

    def test_led_set_color_without_blink_rack2_board2(self):
        """SNMP read/write of LED. Sad case.
        NOTE: If a write fails or the write back to original fails, this test may be
        non-reentrant.
        """
        # Make sure the device is there.
        logger.debug('test_led_set_color_without_blink_rack2_board2')
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

    def test_led_set_invalid_states_rack2_board2(self):
        """SNMP write of LED. Sad casee.
        NOTE: If a write fails or the write back to original fails, this test may be
        non-reentrant.
        """
        # Make sure the device is there.
        logger.debug('test_led_set_color_without_blink_rack2_board2')
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
