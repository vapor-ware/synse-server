#!/usr/bin/env python
""" Synse API Device Read Tests

    Author:  andrew
    Date:    4/13/2015

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

from vapor_common import http
from vapor_common.errors import VaporHTTPError
from vapor_common.tests.utils.strings import _S

from synse.tests.test_config import PREFIX


class DeviceReadTestCase(unittest.TestCase):
    """ Test device read issues that may arise.
    """
    def test_001_read_zero(self):
        """ Get a zero value for each supported conversion method
        """
        r = http.get(PREFIX + '/read/thermistor/rack_1/00000014/01FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        # self.assertEqual(response['device_raw'], 0)
        self.assertEqual(response['temperature_c'], 131.29)

        r = http.get(PREFIX + '/read/humidity/rack_1/00000014/02FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        # self.assertEqual(response['device_raw'], 0)
        self.assertEqual(response['temperature_c'], -40)
        self.assertEqual(response['humidity'], 0)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/rack_1/none/00000014/03FF')

        self.assertEqual(ctx.exception.status, 500)

    def test_002_read_mid(self):
        """ Get a midpoint value for each supported conversion method
        """
        r = http.get(PREFIX + '/read/thermistor/rack_1/00000014/04FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        # self.assertEqual(response['device_raw'], 32768)
        self.assertEqual(response['temperature_c'], -4173.97)

        r = http.get(PREFIX + '/read/humidity/rack_1/00000014/05FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        # self.assertEqual(response['device_raw'], 65535)            # 0x0000FFFF
        self.assertAlmostEqual(response['temperature_c'], 125, 1)  # max
        self.assertEqual(response['humidity'], 0)  # zero

        r = http.get(PREFIX + '/read/humidity/rack_1/00000014/05FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        # self.assertEqual(response['device_raw'], 4294901760)     # 0xFFFF0000
        self.assertEqual(response['temperature_c'], -40)  # zero
        self.assertAlmostEqual(response['humidity'], 100, 1)  # max

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/rack_1/none/00000014/06FF')

        self.assertEqual(ctx.exception.status, 500)

    def test_003_read_8byte_max(self):
        """ Get a max value for each supported conversion method
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/thermistor/rack_1/00000014/07FF')

        self.assertEqual(ctx.exception.status, 500)  # 65535 was the value

        r = http.get(PREFIX + '/read/thermistor/rack_1/00000014/08FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        # self.assertEqual(response['device_raw'], 65534)
        self.assertAlmostEqual(response['temperature_c'], -8466.32, 1)

        r = http.get(PREFIX + '/read/humidity/rack_1/00000014/09FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        # self.assertEqual(response['device_raw'], 4294967295)
        self.assertAlmostEqual(response['temperature_c'], 125, 1)
        self.assertAlmostEqual(response['humidity'], 100, 1)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/rack_1/none/00000014/0AFF')

        self.assertEqual(ctx.exception.status, 500)

    def test_004_weird_data(self):
        """ What happens when a lot of integer data are returned?
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/thermistor/rack_1/00000014/0BFF')

        self.assertEqual(ctx.exception.status, 500)  # we read something super weird for thermistor, so error

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/humidity/rack_1/00000014/0CFF')

        self.assertEqual(ctx.exception.status, 500)  # we read something super weird for humidity, so error

    def test_005_bad_data(self):
        """ What happens when bad byte data are received.  What happens when
        there's a bad checksum or trailer?
        """
        # bad bytes
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/thermistor/rack_1/00000014/0DFF')

        self.assertEqual(ctx.exception.status, 500)

        # bad trailer
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/thermistor/rack_1/00000014/0EFF')

        self.assertEqual(ctx.exception.status, 500)

        # bad checksum
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/thermistor/rack_1/00000014/0FFF')

        self.assertEqual(ctx.exception.status, 500)

    def test_006_no_data(self):
        """ Timeout.
        """
        # timeout
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/rack_1/none/00000014/10FF')

        self.assertEqual(ctx.exception.status, 500)

    def test_007_board_id_representation(self):
        """ Test reading while specifying different representations (same value) for
        the board id
        """
        r = http.get(PREFIX + '/read/thermistor/rack_1/14/04FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        # self.assertEqual(response['device_raw'], 32768)
        self.assertEqual(response['temperature_c'], -4173.97)

        r = http.get(PREFIX + '/read/thermistor/rack_1/014/04FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        # self.assertEqual(response['device_raw'], 32768)
        self.assertEqual(response['temperature_c'], -4173.97)

        r = http.get(PREFIX + '/read/thermistor/rack_1/00014/04FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        # self.assertEqual(response['device_raw'], 32768)
        self.assertEqual(response['temperature_c'], -4173.97)

        r = http.get(PREFIX + '/read/thermistor/rack_1/000014/04FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        # self.assertEqual(response['device_raw'], 32768)
        self.assertEqual(response['temperature_c'], -4173.97)

        r = http.get(PREFIX + '/read/thermistor/rack_1/00000014/04FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        # self.assertEqual(response['device_raw'], 32768)
        self.assertEqual(response['temperature_c'], -4173.97)

    def test_008_device_id_representation(self):
        """ Test reading while specifying different representations (same value) for
        the device id
        """
        r = http.get(PREFIX + '/read/thermistor/rack_1/00000014/4FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        # self.assertEqual(response['device_raw'], 32768)
        self.assertEqual(response['temperature_c'], -4173.97)

        r = http.get(PREFIX + '/read/thermistor/rack_1/00000014/04FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        # self.assertEqual(response['device_raw'], 32768)
        self.assertEqual(response['temperature_c'], -4173.97)

        r = http.get(PREFIX + '/read/thermistor/rack_1/00000014/00004FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        # self.assertEqual(response['device_raw'], 32768)
        self.assertEqual(response['temperature_c'], -4173.97)

    def test_009_rack_id_representation(self):
        """ Test reading while specifying different values for the rack_id
        """
        r = http.get(PREFIX + '/read/thermistor/rack_1/00000014/04FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], -4173.97)

        r = http.get(PREFIX + '/read/thermistor/STRING_NOT_RELATED_TO_RACK_AT_ALL/00000014/04FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], -4173.97)

        r = http.get(PREFIX + '/read/thermistor/STRING WITH SPACES/00000014/04FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], -4173.97)

        r = http.get(PREFIX + '/read/thermistor/123456789/00000014/04FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], -4173.97)

        r = http.get(PREFIX + '/read/thermistor/123.456/00000014/04FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], -4173.97)

        r = http.get(PREFIX + '/read/thermistor/-987654321/00000014/04FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], -4173.97)

        r = http.get(PREFIX + '/read/thermistor/acceptable_chars_\@$-_.+!*\'(),^&~:;|}{}][]>=<>/00000014/04FF')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], -4173.97)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/thermistor//00000014/04FF')

        self.assertEqual(ctx.exception.status, 404)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/thermistor/bad_char?/00000014/04FF')

        self.assertEqual(ctx.exception.status, 404)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/thermistor/bad_char#/00000014/04FF')

        self.assertEqual(ctx.exception.status, 404)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/thermistor/bad_char%/00000014/04FF')

        self.assertEqual(ctx.exception.status, 400)

    def test_010_read_board_id_invalid(self):
        """ Test read while specifying different invalid representations for
        the board id to ensure out-of-range values are not handled (e.g. set bits on packet that should not be set)
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/thermistor/rack_1/FFFFFFFF/1FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/thermistor/rack_1/FFFFFFFFFFFFFFFF/1FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/thermistor/rack_1/20000000/00001FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/thermistor/rack_1/10000000/00001FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/thermistor/rack_1/-10000000/00001FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/thermistor/rack_1/-10000000/-00001FF')

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/thermistor/rack_1/10000000/-00001FF')

        self.assertEqual(ctx.exception.status, 500)

    def test_011_read_temperature_valid(self):
        """ Read a valid temperature value (30.03)
        """
        r = http.get(PREFIX + '/read/temperature/rack_1/00000015/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 30.03)

    def test_012_read_temperature_invalid(self):
        """ Read invalid temperature value (invalid)
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/temperature/rack_1/00000015/0002')

        self.assertEqual(ctx.exception.status, 500)

    def test_013_read_temperature_float_string_valid(self):
        """ Read a valid temperature value (30.03)
        """
        r = http.get(PREFIX + '/read/temperature/rack_1/00000015/0003')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 30.03)

    def test_014_read_temperature_int_string_valid(self):
        """ Read a valid temperature value (30)
        """
        r = http.get(PREFIX + '/read/temperature/rack_1/00000015/0004')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 30)

    def test_015_read_temperature_int_valid(self):
        """ Read a valid temperature value (30.03)
        """
        r = http.get(PREFIX + '/read/temperature/rack_1/00000015/0005')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 30)

    def test_016_read_pressure_valid(self):
        """ Read a valid pressure value (0.00)
        """
        r = http.get(PREFIX + '/read/pressure/rack_1/00000016/0001')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response[_S.PRESSURE_PA], 0.00)

    def test_017_read_pressure_invalid(self):
        """ Read invalid pressure value (invalid)
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + '/read/rack_1/pressure/00000016/0002')

        self.assertEqual(ctx.exception.status, 500)

    def test_018_read_pressure_float_string_valid(self):
        """ Read a valid pressure value (-0.12)
        """
        r = http.get(PREFIX + '/read/pressure/rack_1/00000016/0003')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response[_S.PRESSURE_PA], -0.12)

    def test_019_read_pressure_int_string_valid(self):
        """ Read a valid pressure value (1)
        """
        r = http.get(PREFIX + '/read/pressure/rack_1/00000016/0004')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response[_S.PRESSURE_PA], 1)

    def test_020_read_pressure_int_valid(self):
        """ Read a valid pressure value (-1)
        """
        r = http.get(PREFIX + '/read/pressure/rack_1/00000016/0005')
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response[_S.PRESSURE_PA], -1)
