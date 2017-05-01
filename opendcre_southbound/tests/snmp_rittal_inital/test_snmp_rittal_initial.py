#!/usr/bin/env python
""" OpenDCRE Southbound SNMP Device Registration Tests

    \\//
     \/apor IO
"""

import json
import logging
import unittest

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
RACK_3 = 'rack_3'
SNMP_EMULATOR_RITTAL_CMC_III_COOLING = 'snmp-emulator-rittal-cmc-iii-cooling'
SNMP_EMULATOR_RITTAL_CMC_III_MONITOR = 'snmp-emulator-rittal-cmc-iii-monitor'
SNMP_EMULATOR_RITTAL_UPS = 'snmp-emulator-rittal-ups'

# endregion


class SnmpRittalInitialTestCase(OpenDcreHttpTest):
    """Testing for the initial walks we received from Rittal."""

    # region Scan Helpers

    def _verify_rack1_scan(self, response):
        """
        Common area to validate valid scan all results.
        :param response: The valid scan all response to verify.
        """
        # Get the first rack.
        rack = self._get_rack_by_id(response, RACK_1)
        self._verify_common_rack_fields(rack)

        # Verify rack_id.
        self.assertEquals(RACK_1, rack[_S.RACK_ID])

        # Verify hostnames.
        hostnames = rack[_S.HOSTNAMES]
        self.assertEquals(1, len(hostnames))
        self.assertEquals(SNMP_EMULATOR_RITTAL_CMC_III_MONITOR, hostnames[0])

        # Verify ip_addresses.
        ip_addresses = rack[_S.IP_ADDRESSES]
        self.assertEquals(1, len(ip_addresses))
        self.assertEquals(SNMP_EMULATOR_RITTAL_CMC_III_MONITOR, ip_addresses[0])

        # Verify boards.
        boards = rack[_S.BOARDS]
        self.assertEqual(1, len(boards))

        board = boards[0]
        self._verify_common_board_fields(board)

        # Verify board id.
        board_id = board[_S.BOARD_ID]
        self.assertEquals(BOARD_60000000, board_id)

        # Verify devices.
        devices = board[_S.DEVICES]
        self.assertEqual(10, len(devices))

        # Verify each device.
        self._verify_device(devices[0], '0000', _S.DEVICE_TYPE_HUMIDITY, _S.DEVICE_TYPE_HUMIDITY)
        self._verify_device(devices[1], '0001', _S.DEVICE_TYPE_VOLTAGE, _S.DEVICE_TYPE_VOLTAGE)
        self._verify_device(devices[2], '0002', _S.DEVICE_TYPE_VOLTAGE, _S.DEVICE_TYPE_VOLTAGE)
        self._verify_device(devices[3], '0003', _S.DEVICE_TYPE_TEMPERATURE, _S.DEVICE_TYPE_TEMPERATURE)
        self._verify_device(devices[4], '0004', _S.DEVICE_TYPE_CURRENT, _S.DEVICE_TYPE_CURRENT)
        self._verify_device(devices[5], '0005', _S.DEVICE_TYPE_CURRENT, _S.DEVICE_TYPE_CURRENT)
        self._verify_device(devices[6], '0006', _S.DEVICE_TYPE_HUMIDITY, _S.DEVICE_TYPE_HUMIDITY)
        self._verify_device(devices[7], '0007', _S.DEVICE_TYPE_TEMPERATURE, _S.DEVICE_TYPE_TEMPERATURE)
        self._verify_device(devices[8], '0008', _S.DEVICE_TYPE_VOLTAGE, _S.DEVICE_TYPE_VOLTAGE)
        self._verify_device(devices[9], '0009', _S.DEVICE_TYPE_HUMIDITY, _S.DEVICE_TYPE_HUMIDITY)

    def _verify_rack2_scan(self, response):
        """
        Common area to validate valid scan all results.
        :param response: The valid scan all response to verify.
        """
        # Get the first rack.
        rack = self._get_rack_by_id(response, RACK_2)
        self._verify_common_rack_fields(rack)

        # Verify rack_id.
        self.assertEquals(RACK_2, rack[_S.RACK_ID])

        # Verify hostnames.
        hostnames = rack[_S.HOSTNAMES]
        self.assertEquals(1, len(hostnames))
        self.assertEquals(SNMP_EMULATOR_RITTAL_CMC_III_COOLING, hostnames[0])

        # Verify ip_addresses.
        ip_addresses = rack[_S.IP_ADDRESSES]
        self.assertEquals(1, len(ip_addresses))
        self.assertEquals(SNMP_EMULATOR_RITTAL_CMC_III_COOLING, ip_addresses[0])

        # Verify boards.
        boards = rack[_S.BOARDS]
        self.assertEqual(1, len(boards))

        board = boards[0]
        self._verify_common_board_fields(board)

        # Verify board id.
        board_id = board[_S.BOARD_ID]
        self.assertEquals(BOARD_60000001, board_id)

        # Verify devices.
        devices = board[_S.DEVICES]
        self.assertEqual(33, len(devices))

        # Verify each device.
        self._verify_device(devices[0], '0000', _S.DEVICE_TYPE_VOLTAGE, _S.DEVICE_TYPE_VOLTAGE)
        self._verify_device(devices[1], '0001', _S.DEVICE_TYPE_VOLTAGE, _S.DEVICE_TYPE_VOLTAGE)
        self._verify_device(devices[2], '0002', _S.DEVICE_TYPE_TEMPERATURE, _S.DEVICE_TYPE_TEMPERATURE)
        self._verify_device(devices[3], '0003', _S.DEVICE_TYPE_CURRENT, _S.DEVICE_TYPE_CURRENT)
        self._verify_device(devices[4], '0004', _S.DEVICE_TYPE_CURRENT, _S.DEVICE_TYPE_CURRENT)
        self._verify_device(devices[5], '0005', _S.DEVICE_TYPE_HUMIDITY, _S.DEVICE_TYPE_HUMIDITY)
        self._verify_device(devices[6], '0006', _S.DEVICE_TYPE_TEMPERATURE, _S.DEVICE_TYPE_TEMPERATURE)
        self._verify_device(devices[7], '0007', _S.DEVICE_TYPE_VOLTAGE, _S.DEVICE_TYPE_VOLTAGE)
        self._verify_device(devices[8], '0008', _S.DEVICE_TYPE_HUMIDITY, _S.DEVICE_TYPE_HUMIDITY)
        self._verify_device(devices[9], '0009', _S.DEVICE_TYPE_TEMPERATURE, _S.DEVICE_TYPE_TEMPERATURE)
        self._verify_device(devices[10], '000a', _S.DEVICE_TYPE_HUMIDITY, _S.DEVICE_TYPE_HUMIDITY)
        self._verify_device(devices[11], '000b', _S.DEVICE_TYPE_HUMIDITY, _S.DEVICE_TYPE_HUMIDITY)
        self._verify_device(devices[12], '000c', _S.DEVICE_TYPE_HUMIDITY, _S.DEVICE_TYPE_HUMIDITY)
        self._verify_device(devices[13], '000d', _S.DEVICE_TYPE_HUMIDITY, _S.DEVICE_TYPE_HUMIDITY)
        self._verify_device(devices[14], '000e', _S.DEVICE_TYPE_TEMPERATURE, _S.DEVICE_TYPE_TEMPERATURE)
        self._verify_device(devices[15], '000f', _S.DEVICE_TYPE_TEMPERATURE, _S.DEVICE_TYPE_TEMPERATURE)
        self._verify_device(devices[16], '0010', _S.DEVICE_TYPE_TEMPERATURE, _S.DEVICE_TYPE_TEMPERATURE)
        self._verify_device(devices[17], '0011', _S.DEVICE_TYPE_HUMIDITY, _S.DEVICE_TYPE_HUMIDITY)
        self._verify_device(devices[18], '0012', _S.DEVICE_TYPE_TEMPERATURE, _S.DEVICE_TYPE_TEMPERATURE)
        self._verify_device(devices[19], '0013', _S.DEVICE_TYPE_HUMIDITY, _S.DEVICE_TYPE_HUMIDITY)
        self._verify_device(devices[20], '0014', _S.DEVICE_TYPE_TEMPERATURE, _S.DEVICE_TYPE_TEMPERATURE)
        self._verify_device(devices[21], '0015', _S.DEVICE_TYPE_TEMPERATURE, _S.DEVICE_TYPE_TEMPERATURE)
        self._verify_device(devices[22], '0016', _S.DEVICE_TYPE_TEMPERATURE, _S.DEVICE_TYPE_TEMPERATURE)
        self._verify_device(devices[23], '0017', _S.DEVICE_TYPE_TEMPERATURE, _S.DEVICE_TYPE_TEMPERATURE)
        self._verify_device(devices[24], '0018', _S.DEVICE_TYPE_TEMPERATURE, _S.DEVICE_TYPE_TEMPERATURE)
        self._verify_device(devices[25], '0019', _S.DEVICE_TYPE_TEMPERATURE, _S.DEVICE_TYPE_TEMPERATURE)
        self._verify_device(devices[26], '001a', _S.DEVICE_TYPE_TEMPERATURE, _S.DEVICE_TYPE_TEMPERATURE)
        self._verify_device(devices[27], '001b', _S.DEVICE_TYPE_TEMPERATURE, _S.DEVICE_TYPE_TEMPERATURE)
        self._verify_device(devices[28], '001c', _S.DEVICE_TYPE_TEMPERATURE, _S.DEVICE_TYPE_TEMPERATURE)
        self._verify_device(devices[29], '001d', _S.DEVICE_TYPE_TEMPERATURE, _S.DEVICE_TYPE_TEMPERATURE)
        self._verify_device(devices[30], '001e', _S.DEVICE_TYPE_TEMPERATURE, _S.DEVICE_TYPE_TEMPERATURE)
        self._verify_device(devices[31], '001f', _S.DEVICE_TYPE_POWER, _S.DEVICE_TYPE_POWER)
        self._verify_device(devices[32], '0020', _S.DEVICE_TYPE_HUMIDITY, _S.DEVICE_TYPE_HUMIDITY)

    def _verify_rack3_scan(self, response):
        """
        Common area to validate valid scan all results.
        :param response: The valid scan all response to verify.
        """
        # Get the first rack.
        rack = self._get_rack_by_id(response, RACK_3)
        self._verify_common_rack_fields(rack)

        # Verify rack_id.
        self.assertEquals(RACK_3, rack[_S.RACK_ID])

        # Verify hostnames.
        hostnames = rack[_S.HOSTNAMES]
        self.assertEquals(1, len(hostnames))
        self.assertEquals(SNMP_EMULATOR_RITTAL_UPS, hostnames[0])

        # Verify ip_addresses.
        ip_addresses = rack[_S.IP_ADDRESSES]
        self.assertEquals(1, len(ip_addresses))
        self.assertEquals(SNMP_EMULATOR_RITTAL_UPS, ip_addresses[0])

        # Verify boards.
        boards = rack[_S.BOARDS]
        self.assertEqual(1, len(boards))

        board = boards[0]
        self._verify_common_board_fields(board)

        # Verify board id.
        board_id = board[_S.BOARD_ID]
        self.assertEquals(BOARD_60000002, board_id)

        # Verify devices.
        devices = board[_S.DEVICES]
        self.assertEqual(36, len(devices))

        # Verify each device.
        self._verify_device(devices[0], '0000', 'battery0000', _S.DEVICE_TYPE_CURRENT)
        self._verify_device(devices[1], '0001', 'battery0000', _S.DEVICE_TYPE_TEMPERATURE)
        self._verify_device(devices[2], '0002', 'battery0000', _S.DEVICE_TYPE_VOLTAGE)

        self._verify_device(devices[3], '0003', 'input0000', _S.DEVICE_TYPE_CURRENT)
        self._verify_device(devices[4], '0004', 'input0000', _S.DEVICE_TYPE_FREQUENCY)
        self._verify_device(devices[5], '0005', 'input0000', _S.DEVICE_TYPE_VOLTAGE)
        self._verify_device(devices[6], '0006', 'input0000', _S.DEVICE_TYPE_POWER)

        self._verify_device(devices[7], '0007', 'input0001', _S.DEVICE_TYPE_CURRENT)
        self._verify_device(devices[8], '0008', 'input0001', _S.DEVICE_TYPE_FREQUENCY)
        self._verify_device(devices[9], '0009', 'input0001', _S.DEVICE_TYPE_VOLTAGE)
        self._verify_device(devices[10], '000a', 'input0001', _S.DEVICE_TYPE_POWER)

        self._verify_device(devices[11], '000b', 'input0002', _S.DEVICE_TYPE_CURRENT)
        self._verify_device(devices[12], '000c', 'input0002', _S.DEVICE_TYPE_FREQUENCY)
        self._verify_device(devices[13], '000d', 'input0002', _S.DEVICE_TYPE_VOLTAGE)
        self._verify_device(devices[14], '000e', 'input0002', _S.DEVICE_TYPE_POWER)

        self._verify_device(devices[15], '000f', 'output0000', _S.DEVICE_TYPE_CURRENT)
        self._verify_device(devices[16], '0010', 'output0000', _S.DEVICE_TYPE_PERCENT_LOAD)
        self._verify_device(devices[17], '0011', 'output0000', _S.DEVICE_TYPE_VOLTAGE)
        self._verify_device(devices[18], '0012', 'output0000', _S.DEVICE_TYPE_POWER)

        self._verify_device(devices[19], '0013', 'output0001', _S.DEVICE_TYPE_CURRENT)
        self._verify_device(devices[20], '0014', 'output0001', _S.DEVICE_TYPE_PERCENT_LOAD)
        self._verify_device(devices[21], '0015', 'output0001', _S.DEVICE_TYPE_VOLTAGE)
        self._verify_device(devices[22], '0016', 'output0001', _S.DEVICE_TYPE_POWER)

        self._verify_device(devices[23], '0017', 'output0002', _S.DEVICE_TYPE_CURRENT)
        self._verify_device(devices[24], '0018', 'output0002', _S.DEVICE_TYPE_PERCENT_LOAD)
        self._verify_device(devices[25], '0019', 'output0002', _S.DEVICE_TYPE_VOLTAGE)
        self._verify_device(devices[26], '001a', 'output0002', _S.DEVICE_TYPE_POWER)

        self._verify_device(devices[27], '001b', 'bypass0000', _S.DEVICE_TYPE_CURRENT)
        self._verify_device(devices[28], '001c', 'bypass0000', _S.DEVICE_TYPE_VOLTAGE)
        self._verify_device(devices[29], '001d', 'bypass0000', _S.DEVICE_TYPE_POWER)

        self._verify_device(devices[30], '001e', 'bypass0001', _S.DEVICE_TYPE_CURRENT)
        self._verify_device(devices[31], '001f', 'bypass0001', _S.DEVICE_TYPE_VOLTAGE)
        self._verify_device(devices[32], '0020', 'bypass0001', _S.DEVICE_TYPE_POWER)

        self._verify_device(devices[33], '0021', 'bypass0002', _S.DEVICE_TYPE_CURRENT)
        self._verify_device(devices[34], '0022', 'bypass0002', _S.DEVICE_TYPE_VOLTAGE)
        self._verify_device(devices[35], '0023', 'bypass0002', _S.DEVICE_TYPE_POWER)

    def _verify_valid_scan_all(self, response, expected_rack_count):
        """
        Common area to validate valid scan all results.
        :param response: The valid scan all response to verify.
        """
        self._verify_expected_rack_count(response, expected_rack_count)
        self._verify_rack1_scan(response)
        self._verify_rack2_scan(response)
        self._verify_rack3_scan(response)

    # endregion

    # region Scan All

    @unittest.skip('https://github.com/vapor-ware/opendcre-core/issues/641')
    def test_scan_all_force(self):
        """ Test scan all force expecting happy results.
        """
        # This can fail under memory pressure (Docker is a memory leak),
        # so upped the timeout.
        r = http.get(Uri.create(_S.URI_SCAN_FORCE), timeout=40)
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))

        self._verify_valid_scan_all(response, 3)

    def test_scan_all(self):
        """ Test scan all expecting happy results.
        """
        r = http.get(Uri.create(_S.URI_SCAN), timeout=15)
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))

        self._verify_valid_scan_all(response, 3)

    # endregion

    # region Scan

    def test_scan_by_rack1(self):
        """ Test scan rack_1 expecting happy results.
        """
        r = http.get(Uri.create(_S.URI_SCAN, RACK_1), timeout=10)
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

    def test_scan_by_rack3(self):
        """ Test scan rack_3 expecting happy results.
        """
        r = http.get(Uri.create(_S.URI_SCAN, RACK_3))
        self.assertTrue(http.request_ok(r.status_code))

        response = r.json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))

        self._verify_expected_rack_count(response, 1)
        self._verify_rack3_scan(response)

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

    # region Version

    # Sad cases are covered elsewhere. Version code is common in SnmpServerBase.
    # Let's make sure the happy cases work though.

    def test_version_rack1(self):
        """SNMP version testing. Happy case."""
        response = http.get(Uri.create(_S.URI_VERSION, RACK_1, BOARD_60000000)).json()
        self._verify_version_snmp(response, _S.SNMP_V2C)

    def test_version_rack2(self):
        """SNMP version testing. Happy case."""
        response = http.get(Uri.create(_S.URI_VERSION, RACK_2, BOARD_60000001)).json()
        self._verify_version_snmp(response, _S.SNMP_V2C)

    def test_version_rack3(self):
        """SNMP version testing. Happy case."""
        response = http.get(Uri.create(_S.URI_VERSION, RACK_3, BOARD_60000002)).json()
        self._verify_version_snmp(response, _S.SNMP_V2C)

    # endregion

    # region Read

    def test_read_temperature_rack1(self):
        """SNMP read of temperature variable. Happy case."""
        logger.debug('test_read_temperature_rack1')
        response = http.get(
            Uri.read_temperature(RACK_1, BOARD_60000000, '0003')).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_read_temperature_response(response, _S.OK, [], 20.3)

    def test_read_voltage_rack1(self):
        """SNMP read of voltage variable. Happy case."""
        logger.debug('test_read_voltage_rack1')
        response = http.get(Uri.read_voltage(RACK_1, BOARD_60000000, '0001')).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_read_voltage_response(response, _S.OK, [], 3.31)

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
        don't support humidity sensors yet. Sad case."""
        try:
            http.get(Uri.read_humidity(RACK_1, BOARD_60000000, '0003'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(
                e, 500, _S.ERROR_DEVICE_TYPE_NOT_SUPPORTED.format(_S.DEVICE_TYPE_HUMIDITY))

    def test_read_wrong_device_type_in_url_rack1(self):
        """Read a valid device, but wrong type in the url.
        Read voltage, but it's a temperature sensor. Sad case."""
        try:
            http.get(Uri.read_voltage(RACK_1, BOARD_60000000, '0003'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(
                e, 500, _S.ERROR_WRONG_DEVICE_TYPE.format(_S.DEVICE_TYPE_VOLTAGE, _S.DEVICE_TYPE_TEMPERATURE))

    # Rack 2

    def test_read_temperature_rack2(self):
        """SNMP read of temperature variable. Happy case."""
        logger.debug('test_read_temperature_rack2')
        response = http.get(
            Uri.read_temperature(RACK_2, BOARD_60000001, '0002')).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_read_temperature_response(response, _S.OK, [], 18.8)

    def test_read_voltage_rack2(self):
        """SNMP read of voltage variable. Happy case."""
        logger.debug('test_read_voltage_rack2')
        response = http.get(Uri.read_voltage(RACK_2, BOARD_60000001, '0000')).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_read_voltage_response(response, _S.OK, [], 3.31)

    def test_read_board_does_not_exist_rack12(self):
        """Test read where board does not exist. Sad case."""
        try:
            http.get(Uri.read_temperature(RACK_2, '60000006', '0001'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_NO_REGISTERED_DEVICE_FOR_BOARD.format(int('60000006', 16)))

    def test_read_device_does_not_exist_rack2(self):
        """Test read where device does not exist. Sad case."""
        try:
            http.get(Uri.read_temperature(RACK_2, BOARD_60000001, 'F001'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_NO_DEVICE_WITH_ID.format('f001'))

    def test_read_device_not_yet_supported_rack2(self):
        """Test read device not yet supported. Board and device are there, we just
        don't support humidity sensors yet. Sad case."""
        try:
            http.get(Uri.read_humidity(RACK_2, BOARD_60000001, '0005'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(
                e, 500, _S.ERROR_DEVICE_TYPE_NOT_SUPPORTED.format(_S.DEVICE_TYPE_HUMIDITY))

    def test_read_wrong_device_type_in_url_rack2(self):
        """Read a valid device, but wrong type in the url.
        Read voltage, but it's a temperature sensor. Sad case."""
        try:
            http.get(Uri.read_voltage(RACK_2, BOARD_60000001, '0006'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(
                e, 500, _S.ERROR_WRONG_DEVICE_TYPE.format(_S.DEVICE_TYPE_VOLTAGE, _S.DEVICE_TYPE_TEMPERATURE))

    # Rack 3

    def test_read_temperature_rack3_battery(self):
        """SNMP read of temperature variable. Happy case."""
        logger.debug('test_read_temperature_rack3_battery')
        response = http.get(
            Uri.read_temperature(RACK_3, BOARD_60000002, '0001')).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_read_temperature_response(response, _S.OK, [], 25)

    def test_read_voltage_rack3_battery(self):
        """SNMP read of voltage variable. Happy case."""
        logger.debug('test_read_voltage_rack3_battery')
        response = http.get(Uri.read_voltage(RACK_3, BOARD_60000002, '0000')).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_read_voltage_response(response, _S.OK, [], 339.4)

    def test_read_voltage_rack3_input(self):
        """SNMP read of voltage variable. Happy case."""
        logger.debug('test_read_voltage_rack3_input')
        response = http.get(Uri.read_voltage(RACK_3, BOARD_60000002, '0005')).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_read_voltage_response(response, _S.OK, [], 0)

    def test_read_voltage_rack3_output(self):
        """SNMP read of voltage variable. Happy case."""
        logger.debug('test_read_voltage_rack3_output')
        response = http.get(Uri.read_voltage(RACK_3, BOARD_60000002, '0015')).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_read_voltage_response(response, _S.OK, [], 230)

    def test_read_voltage_rack3_bypass(self):
        """SNMP read of voltage variable. Happy case."""
        logger.debug('test_read_voltage_rack3_bypass')
        response = http.get(Uri.read_voltage(RACK_3, BOARD_60000002, '0022')).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_read_voltage_response(response, _S.OK, [], 0)


    # endregion

    # region Power reads

    # No power devices on rack 1, so rack 2.

    def test_power_read_rack2(self):
        logger.debug('test_power_read_rack2')
        base_uri = Uri.create(_S.URI_POWER, RACK_2, BOARD_60000001, '001f')
        response = http.get(base_uri).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_power_response(response, 19842, False, True, _S.ON)

    def test_power_read_rack3_input(self):
        logger.debug('test_power_read_rack3_input')
        base_uri = Uri.create(_S.URI_POWER, RACK_3, BOARD_60000002, '0005')
        response = http.get(base_uri).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_power_response(response, 0, False, True, _S.OFF)

    def test_power_read_rack3_output(self):
        logger.debug('test_power_read_rack3_output')
        base_uri = Uri.create(_S.URI_POWER, RACK_3, BOARD_60000002, '0015')
        response = http.get(base_uri).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_power_response(response, 1154, False, True, _S.ON)

    def test_power_read_rack3_input_2(self):
        logger.debug('test_power_read_rack3_input')
        base_uri = Uri.create(_S.URI_POWER, RACK_3, BOARD_60000002, '0022')
        response = http.get(base_uri).json()
        logger.debug(json.dumps(response, sort_keys=True, indent=4, separators=(',', ': ')))
        self._verify_power_response(response, 0, False, True, _S.OFF)

    # Sad cases

    def test_power_board_does_not_exist_rack1(self):
        """Test power where board does not exist. Sad case."""
        try:
            http.get(Uri.create(_S.URI_POWER, RACK_1, '60000006', '0002'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_NO_REGISTERED_DEVICE_FOR_BOARD.format(int('60000006', 16)))

    def test_power_device_does_not_exist_rack1(self):
        """Test power where device does not exist. Sad case."""
        try:
            http.get(Uri.create(_S.URI_POWER, RACK_1, BOARD_60000000, 'F001'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_NO_DEVICE_WITH_ID.format('f001'))

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
            http.get(Uri.create(_S.URI_POWER, RACK_2, BOARD_60000000, 'F001'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_NO_DEVICE_WITH_ID.format('f001'))

    def test_power_write_rack2(self):
        """Test power write where the underlying device does not support it. Sad case."""
        try:
            http.get(Uri.create(_S.URI_POWER, RACK_2, BOARD_60000001, '001f', _S.ON))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(
                e, 500, _S.ERROR_DEVICE_DOES_NOT_SUPPORT_SETTING.format(_S.DEVICE_TYPE_POWER))

    def test_power_board_does_not_exist_rack3(self):
        """Test power where board does not exist. Sad case."""
        try:
            http.get(Uri.create(_S.URI_POWER, RACK_3, '60000006', '0002'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_NO_REGISTERED_DEVICE_FOR_BOARD.format(int('60000006', 16)))

    def test_power_device_does_not_exist_rack23(self):
        """Test power where device does not exist. Sad case."""
        try:
            http.get(Uri.create(_S.URI_POWER, RACK_3, BOARD_60000000, 'F001'))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(e, 500, _S.ERROR_NO_DEVICE_WITH_ID.format('f001'))

    def test_power_write_rack3(self):
        """Test power write where the underlying device does not support it. Sad case."""
        try:
            http.get(Uri.create(_S.URI_POWER, RACK_3, BOARD_60000000, '0005', _S.ON))
            self.fail(EXPECTED_VAPOR_HTTP_ERROR)

        except VaporHTTPError as e:
            self._verify_vapor_http_error(
                e, 500, _S.ERROR_DEVICE_DOES_NOT_SUPPORT_SETTING.format(_S.DEVICE_TYPE_POWER))

    # endregion
