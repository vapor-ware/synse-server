#!/usr/bin/env python
""" VaporCORE Southbound API Battery Tests

    Author:  andrew
    Date:    6/24/2016

    \\//
     \/apor IO
"""
import unittest

from opendcre_southbound.tests.test_config import PREFIX
from vapor_common import http
from vapor_common.errors import VaporHTTPError


class VaporBatteryTestCase(unittest.TestCase):
    """ Battery status tests.
    """

    def test_001_get_power_status(self):
        # expected raw 0
        r = http.get(PREFIX + "/power/rack_1/00000061/00001")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()

        self.assertEqual(response["battery_charge_percent"], 100)
        self.assertEqual(response["battery_status"], "charging")

    def test_002_valid_device_invalid_type(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/power/rack_1/0000001E/02FF")

        self.assertEqual(ctx.exception.status, 500)

    def test_003_invalid_device(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/power/rack_1/00000061/03FF")

        self.assertEqual(ctx.exception.status, 500)

    def test_004_invalid_command(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/power/rack_1/00000061/0001/invalid")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/power/rack_1/00000061/0001/cyle")

        self.assertEqual(ctx.exception.status, 500)

        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/power/rack_1/00000061/0101/xxx")

        self.assertEqual(ctx.exception.status, 500)

    def test_005_no_power_data(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/power/rack_1/00000061/0002")

        self.assertEqual(ctx.exception.status, 500)

    def test_006_junk_power_data(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/power/rack_1/00000061/0003")

        self.assertEqual(ctx.exception.status, 500)

    def test_007_power_board_id_representation(self):
        """ Test power status while specifying different representations (same value) for
        the board id
        """
        r = http.get(PREFIX + "/power/rack_1/61/1")
        self.assertTrue(http.request_ok(r.status_code))

        r = http.get(PREFIX + "/power/rack_1/0061/01")
        self.assertTrue(http.request_ok(r.status_code))

        r = http.get(PREFIX + "/power/rack_1/000061/0001")
        self.assertTrue(http.request_ok(r.status_code))

        r = http.get(PREFIX + "/power/rack_1/00000000061/00000001")
        self.assertTrue(http.request_ok(r.status_code))

    def test_008_power_device_id_representation(self):
        """ Test power status while specifying different representations (same value) for
        the board id
        """
        r = http.get(PREFIX + "/power/rack_1/0000001E/1FF")
        self.assertTrue(http.request_ok(r.status_code))

        r = http.get(PREFIX + "/power/rack_1/0000001E/01FF")
        self.assertTrue(http.request_ok(r.status_code))

        r = http.get(PREFIX + "/power/rack_1/0000001E/00001FF")
        self.assertTrue(http.request_ok(r.status_code))

    def test_009_power_board_id_invalid(self):
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

    def test_010_get_power_status(self):
        # expected raw 0
        r = http.get(PREFIX + "/power/rack_1/00000061/00004")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()

        self.assertEqual(response["battery_charge_percent"], 45)
        self.assertEqual(response["battery_status"], "discharging")
