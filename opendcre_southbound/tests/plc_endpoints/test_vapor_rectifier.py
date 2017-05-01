#!/usr/bin/env python
""" VaporCORE Southbound API Rectifier Power Tests

    Author:  andrew
    Date:    2/23/2016

    \\//
     \/apor IO
"""
import unittest

from opendcre_southbound.tests.test_config import PREFIX
from vapor_common import http
from vapor_common.errors import VaporHTTPError


class VaporRectifierTestCase(unittest.TestCase):
    """ Rectifiers status tests.
    """

    def test_001_get_power_status(self):
        # expected raw 0
        r = http.get(PREFIX + "/power/rack_1/00000060/00001")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()

        # reset the emulator to start at 0,0,0,0, or give up after 8 tries
        # (previous iterations of the old power tests leave the emulator mid-stream)
        i = 0
        while response['pmbus_raw'] != '0,0,0,0':
            r = http.get(PREFIX + "/power/rack_1/00000060/0001")
            self.assertTrue(http.request_ok(r.status_code))
            response = r.json()
            i += 1
            self.assertLess(i, 8)

        self.assertEqual(response["pmbus_raw"], "0,0,0,0")
        self.assertEqual(response["power_status"], "on")
        self.assertEqual(response["power_ok"], True)
        self.assertEqual(response["over_current"], False)
        self.assertEqual(response["under_voltage"], False)

        # expected raw 64 (0x40) - when off, power_ok and under_voltage
        # and under_current don't have any meaning
        r = http.get(PREFIX + "/power/rack_1/00000060/0001")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["pmbus_raw"], "64,0,0,0")
        self.assertEqual(response["power_status"], "off")
        self.assertEqual(response["power_ok"], True)
        self.assertEqual(response["over_current"], False)
        self.assertEqual(response["under_voltage"], False)

        # expected raw 2048 (0x800) - power problem but not
        # something related to under voltage or over current condition
        r = http.get(PREFIX + "/power/rack_1/00000060/0001")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["pmbus_raw"], "2048,0,0,0")
        self.assertEqual(response["power_status"], "on")
        self.assertEqual(response["power_ok"], False)
        self.assertEqual(response["over_current"], False)
        self.assertEqual(response["under_voltage"], False)

        # expected raw 2048+8=2056 (0x1010) - power problem due to under voltage
        r = http.get(PREFIX + "/power/rack_1/00000060/0001")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["pmbus_raw"], "2056,0,0,0")
        self.assertEqual(response["power_status"], "on")
        self.assertEqual(response["power_ok"], False)
        self.assertEqual(response["over_current"], False)
        self.assertEqual(response["under_voltage"], True)

        # expected raw 2048+16=2064 (0x1020) - power problem due to over current
        r = http.get(PREFIX + "/power/rack_1/00000060/0001")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["pmbus_raw"], "2064,0,0,0")
        self.assertEqual(response["power_status"], "on")
        self.assertEqual(response["power_ok"], False)
        self.assertEqual(response["over_current"], True)
        self.assertEqual(response["under_voltage"], False)

        # expected raw 2072 (0x1030)
        r = http.get(PREFIX + "/power/rack_1/00000060/0001")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["pmbus_raw"], "2072,0,0,0")
        self.assertEqual(response["power_status"], "on")
        self.assertEqual(response["power_ok"], False)
        self.assertEqual(response["over_current"], True)
        self.assertEqual(response["under_voltage"], True)

    def test_002_valid_device_invalid_type(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/power/rack_1/0000001E/02FF")

        self.assertEqual(ctx.exception.status, 500)

    def test_003_invalid_device(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/power/rack_1/00000060/03FF")

        self.assertEqual(ctx.exception.status, 500)

    def test_004_invalid_command(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/power/rack_1/00000060/0001/invalid")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/power/rack_1/00000060/0001/cyle")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/power/rack_1/00000060/0101/xxx")

        self.assertEqual(ctx.exception.status, 500)

    def test_005_no_power_data(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/power/rack_1/00000060/0002")

        self.assertEqual(ctx.exception.status, 500)

    def test_006_power_board_id_representation(self):
        """ Test power status while specifying different representations (same value) for
        the board id
        """
        r = http.get(PREFIX + "/power/rack_1/60/1")
        self.assertTrue(http.request_ok(r.status_code))

        r = http.get(PREFIX + "/power/rack_1/0060/01")
        self.assertTrue(http.request_ok(r.status_code))

        r = http.get(PREFIX + "/power/rack_1/000060/0001")
        self.assertTrue(http.request_ok(r.status_code))

        r = http.get(PREFIX + "/power/rack_1/00000000060/00000001")
        self.assertTrue(http.request_ok(r.status_code))

    def test_007_power_device_id_representation(self):
        """ Test power status while specifying different representations (same value) for
        the board id
        """
        r = http.get(PREFIX + "/power/rack_1/0000001E/1FF")
        self.assertTrue(http.request_ok(r.status_code))

        r = http.get(PREFIX + "/power/rack_1/0000001E/01FF")
        self.assertTrue(http.request_ok(r.status_code))

        r = http.get(PREFIX + "/power/rack_1/0000001E/00001FF")
        self.assertTrue(http.request_ok(r.status_code))

    def test_008_power_board_id_invalid(self):
        """ Test power status while specifying different invalid representations for
        the board id to ensure out-of-range values are not handled (e.g. set bits on
        packet that should not be set)
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/power/rack_1/FFFFFFFF/0001")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/power/rack_1/FFFFFFFFFFFFFFFF/0001")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/power/rack_1/20000000/00000001")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/power/rack_1/10000000/00000001")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/power/rack_1/x/10000000/0000001")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/power/rack_1/-10000000/0000001")

        self.assertEqual(ctx.exception.status, 500)
