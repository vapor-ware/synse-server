#!/usr/bin/env python
""" Tests for Synse utils' device id helpers.

    Author: Erick Daniszewski
    Date:   19 April 2017

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

import synse.constants as const
import synse.utils as utils


class DeviceIdUtilsTestCase(unittest.TestCase):

    def test_000_normalize_device_id(self):
        """ Test normalizing the device id to a string.
        """
        normalized = utils.normalize_device_id(0x0000)
        self.assertEqual(normalized, '0000')

    def test_001_normalize_device_id(self):
        """ Test normalizing the device id to a string.
        """
        normalized = utils.normalize_device_id(0x0)
        self.assertEqual(normalized, '0000')

    def test_002_normalize_device_id(self):
        """ Test normalizing the device id to a string.
        """
        normalized = utils.normalize_device_id(0xffff)
        self.assertEqual(normalized, 'ffff')

    def test_003_normalize_device_id(self):
        """ Test normalizing the device id to a string.
        """
        normalized = utils.normalize_device_id(0x12)
        self.assertEqual(normalized, '0012')

    def test_004_normalize_device_id(self):
        """ Test normalizing the device id to a string.
        """
        normalized = utils.normalize_device_id('device-string')
        self.assertEqual(normalized, 'device-string')

    def test_005_normalize_device_id(self):
        """ Test normalizing the device id to a string.
        """
        normalized = utils.normalize_device_id('666')
        self.assertEqual(normalized, '666')

    def test_000_device_id_to_string(self):
        """ Test converting an int to its hex string representation.
        """
        hex_string = utils.device_id_to_hex_string(0x0000)
        self.assertEqual(hex_string, '0000')

    def test_001_device_id_to_string(self):
        """ Test converting an int to its hex string representation.
        """
        hex_string = utils.device_id_to_hex_string(0x0)
        self.assertEqual(hex_string, '0000')

    def test_002_device_id_to_string(self):
        """ Test converting an int to its hex string representation.
        """
        hex_string = utils.device_id_to_hex_string(0x123)
        self.assertEqual(hex_string, '0123')

    def test_003_device_id_to_string(self):
        """ Test converting an int to its hex string representation.
        """
        hex_string = utils.device_id_to_hex_string(0xffff)
        self.assertEqual(hex_string, 'ffff')

    def test_004_device_id_to_string(self):
        """ Test converting an int to its hex string representation.

        In this case, the given int is greater than 2 bytes, so it
        should be truncated.
        """
        hex_string = utils.device_id_to_hex_string(0xffffffffff)
        self.assertEqual(hex_string, 'ffffffffff')

    def test_005_device_id_to_string(self):
        """ Test converting an int to its hex string representation.

        In this case, the given parameter is not an int, so the
        conversion should fail.
        """
        with self.assertRaises(ValueError):
            utils.device_id_to_hex_string('not-a-hex-int')

    def test_006_device_id_to_string(self):
        """ Test converting an int to its hex string representation.

        In this case, the given parameter is not an int (though does
        have valid hex string values) so it should fail.
        """
        with self.assertRaises(ValueError):
            utils.device_id_to_hex_string('666')

    def test_009_device_id_to_bytes(self):
        """ Test converting a device_id to bytes.
        """
        device_id = 0xf1e2
        device_id_bytes = utils.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xf1, 0xe2])

        device_id = 0x1
        device_id_bytes = utils.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x1])

        device_id = 0x0000
        device_id_bytes = utils.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x00])

        device_id = 0xffff
        device_id_bytes = utils.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xff, 0xff])

        device_id = 0x123
        device_id_bytes = utils.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x01, 0x23])

    def test_010_device_id_to_bytes(self):
        """ Test converting a device_id to bytes.
        """
        device_id = long(0x00)
        device_id_bytes = utils.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x00])

        device_id = long(0x0f)
        device_id_bytes = utils.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x0f])

        device_id = long(0xffff)
        device_id_bytes = utils.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xff, 0xff])

        device_id = long(0xa1b)
        device_id_bytes = utils.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x0a, 0x1b])

        device_id = long(0xbeef)
        device_id_bytes = utils.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xbe, 0xef])

    def test_011_device_id_to_bytes(self):
        """ Test converting a device_id to bytes.
        """
        device_id = '{0:04x}'.format(0xf1e2)
        device_id_bytes = utils.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xf1, 0xe2])

        device_id = '{0:04x}'.format(0x0)
        device_id_bytes = utils.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x00])

        device_id = '{0:04x}'.format(0xffff)
        device_id_bytes = utils.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xff, 0xff])

        device_id = '{0:04x}'.format(0xabc)
        device_id_bytes = utils.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x0a, 0xbc])

        device_id = '{0:02x}'.format(0x12)
        device_id_bytes = utils.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x12])

    def test_012_device_id_to_bytes(self):
        """ Test converting a device_id to bytes.
        """
        device_id = unicode('{0:04x}'.format(0xf1e2))
        device_id_bytes = utils.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xf1, 0xe2])

        device_id = unicode('{0:04x}'.format(0x0))
        device_id_bytes = utils.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x00])

        device_id = unicode('{0:04x}'.format(0xffff))
        device_id_bytes = utils.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0xff, 0xff])

        device_id = unicode('{0:04x}'.format(0xabc))
        device_id_bytes = utils.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x0a, 0xbc])

        device_id = unicode('{0:02x}'.format(0x12))
        device_id_bytes = utils.device_id_to_bytes(device_id)
        self.assertEqual(device_id_bytes, [0x00, 0x12])

    def test_013_device_id_to_bytes(self):
        """ Test converting a device_id to bytes.
        """
        device_id = [0x00, 0x00]
        device_id_bytes = utils.device_id_to_bytes(device_id)
        self.assertEqual(device_id, device_id_bytes)

        device_id = [0xff, 0xff]
        device_id_bytes = utils.device_id_to_bytes(device_id)
        self.assertEqual(device_id, device_id_bytes)

        device_id = [0x12, 0x34]
        device_id_bytes = utils.device_id_to_bytes(device_id)
        self.assertEqual(device_id, device_id_bytes)

    def test_014_device_id_join_bytes(self):
        """ Test converting a list of device_id bytes into its original value.
        """
        device_id_bytes = [0x00, 0x00]
        device_id = utils.device_id_join_bytes(device_id_bytes)
        self.assertEquals(device_id, 0x0000)

        device_id_bytes = [0xff, 0xff]
        device_id = utils.device_id_join_bytes(device_id_bytes)
        self.assertEquals(device_id, 0xffff)

        device_id_bytes = [0x43, 0x21]
        device_id = utils.device_id_join_bytes(device_id_bytes)
        self.assertEquals(device_id, 0x4321)

        device_id_bytes = [0x00, 0x01]
        device_id = utils.device_id_join_bytes(device_id_bytes)
        self.assertEquals(device_id, 0x1)

        device_id_bytes = [0xa7, 0x2b]
        device_id = utils.device_id_join_bytes(device_id_bytes)
        self.assertEquals(device_id, 0xa72b)

        device_id_bytes = [0xef, 0x00]
        device_id = utils.device_id_join_bytes(device_id_bytes)
        self.assertEquals(device_id, 0xef00)

    def test_015_device_id_join_bytes(self):
        """ Test converting a list of device_id bytes into its original value.
        """
        device_id_bytes = []
        with self.assertRaises(ValueError):
            utils.device_id_join_bytes(device_id_bytes)

        device_id_bytes = [0x12]
        with self.assertRaises(ValueError):
            utils.device_id_join_bytes(device_id_bytes)

        device_id_bytes = [0x12, 0x34, 0x56]
        with self.assertRaises(ValueError):
            utils.device_id_join_bytes(device_id_bytes)

        device_id_bytes = 0x1234
        with self.assertRaises(ValueError):
            utils.device_id_join_bytes(device_id_bytes)

    def test_000_get_device_type_code(self):
        """ Test getting the device type code for a known device.
        """
        device_type = const.DEVICE_VAPOR_LED
        code = utils.get_device_type_code(device_type)
        self.assertEqual(code, const.device_name_codes.get(device_type))

    def test_001_get_device_type_code(self):
        """ Test getting the device type code for an unknown device.
        """
        device_type = 'dummy device'
        code = utils.get_device_type_code(device_type)
        self.assertEqual(code, const.device_name_codes.get(const.DEVICE_NONE))

    def test_002_get_device_type_code(self):
        """ Test getting the device type code for an unknown device.
        """
        device_type = ''
        code = utils.get_device_type_code(device_type)
        self.assertEqual(code, const.device_name_codes.get(const.DEVICE_NONE))

    def test_003_get_device_type_code(self):
        """ Test getting the device type code for an unknown device.
        """
        device_type = ' '
        code = utils.get_device_type_code(device_type)
        self.assertEqual(code, const.device_name_codes.get(const.DEVICE_NONE))

    def test_004_get_device_type_code(self):
        """ Test getting the device type code for an unknown device.
        """
        device_type = None
        code = utils.get_device_type_code(device_type)
        self.assertEqual(code, const.device_name_codes.get(const.DEVICE_NONE))

    def test_005_get_device_type_code(self):
        """ Test getting the device type code for an unknown device.
        """
        device_type = 123
        code = utils.get_device_type_code(device_type)
        self.assertEqual(code, const.device_name_codes.get(const.DEVICE_NONE))

    def test_000_get_device_type_name(self):
        """ Test getting the string value for a given numeric code.
        """
        # see synse/constants.py for all device codes
        code = 0x00
        name = utils.get_device_type_name(code)
        self.assertEqual(name, const.DEVICE_NONE)

    def test_001_get_device_type_name(self):
        """ Test getting the string value for a given numeric code.
        """
        # see synse/constants.py for all device codes
        code = 0x08
        name = utils.get_device_type_name(code)
        self.assertEqual(name, const.DEVICE_VAPOR_LED)

    def test_002_get_device_type_name(self):
        """ Test getting the string value for a given numeric code.
        """
        # see synse/constants.py for all device codes
        code = 0xFFFF
        name = utils.get_device_type_name(code)
        self.assertEqual(name, const.DEVICE_NONE)

    def test_003_get_device_type_name(self):
        """ Test getting the string value for a given numeric code.
        """
        # see synse/constants.py for all device codes
        code = 'unknown'
        name = utils.get_device_type_name(code)
        self.assertEqual(name, const.DEVICE_NONE)

    def test_004_get_device_type_name(self):
        """ Test getting the string value for a given numeric code.
        """
        # see synse/constants.py for all device codes
        code = None
        name = utils.get_device_type_name(code)
        self.assertEqual(name, const.DEVICE_NONE)

    def test_000_get_measure_for_device_type(self):
        """ Test getting a unit of measure for a given device type.
        """
        device_type = const.DEVICE_AIRFLOW
        uom = utils.get_measure_for_device_type(device_type)
        self.assertEqual(uom, const.UOM_AIRFLOW)

    def test_001_get_measure_for_device_type(self):
        """ Test getting a unit of measure for a given device type.
        """
        device_type = const.DEVICE_FAN_SPEED
        uom = utils.get_measure_for_device_type(device_type)
        self.assertEqual(uom, const.UOM_FAN_SPEED)

    def test_002_get_measure_for_device_type(self):
        """ Test getting a unit of measure for a given device type.
        """
        device_type = const.DEVICE_CURRENT
        uom = utils.get_measure_for_device_type(device_type)
        self.assertEqual(uom, None)

    def test_003_get_measure_for_device_type(self):
        """ Test getting a unit of measure for a given device type.
        """
        device_type = 'unknown device name'
        uom = utils.get_measure_for_device_type(device_type)
        self.assertEqual(uom, None)

    def test_004_get_measure_for_device_type(self):
        """ Test getting a unit of measure for a given device type.
        """
        device_type = ' '
        uom = utils.get_measure_for_device_type(device_type)
        self.assertEqual(uom, None)

    def test_005_get_measure_for_device_type(self):
        """ Test getting a unit of measure for a given device type.
        """
        device_type = None
        uom = utils.get_measure_for_device_type(device_type)
        self.assertEqual(uom, None)
