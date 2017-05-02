#!/usr/bin/env python
""" VaporCORE Southbound API Power Tests - Line Noise

    Author:  andrew
    Date:    12/4/2015

    \\//
     \/apor IO
"""
import unittest

from opendcre_southbound.tests.test_config import PREFIX
from vapor_common import http
from vapor_common.errors import VaporHTTPError


class LineNoiseTestCase(unittest.TestCase):
    """ Line Noise Tests - ignore junk at head, positive
    """

    def test_002_junk_head_version(self):
        # expect 200 status, version string
        r = http.get(PREFIX + "/version/rack_1/000000c9")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["firmware_version"], "12345")

    def test_003_junk_head_read(self):
        # expect 200 status, thermistor reading
        r = http.get(PREFIX + "/read/thermistor/rack_1/000000c9/01ff")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        # self.assertEqual(response["device_raw"], 656)
        self.assertEqual(response["temperature_c"], 28.78)

    """
        Line Noise Tests - ignore junk at head, packet too short, all neg
    """

    def test_004_junk_head_tooshort_scan(self):
        # expect 500 status
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/000000ca")

        self.assertEqual(ctx.exception.status, 500)

    def test_005_junk_head_tooshort_version(self):
        # expect 500 status
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/version/rack_1/000000cb")

        self.assertEqual(ctx.exception.status, 500)

    def test_006_junk_head_tooshort_read(self):
        # expect 500 status
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/read/thermistor/rack_1/000000cb/01ff")

        self.assertEqual(ctx.exception.status, 500)

    """
        Line Noise Tests - ignore junk at head, valid packet with junk at tail, positive
    """

    def test_008_junk_head_valid_long_version(self):
        # expect 200 status, version string
        r = http.get(PREFIX + "/version/rack_1/000000cd")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response["firmware_version"], "12345")

    def test_009_junk_head_valid_long_read(self):
        # expect 200 status, thermistor reading
        r = http.get(PREFIX + "/read/thermistor/rack_1/000000cd/01ff")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        # self.assertEqual(response["device_raw"], 656)
        self.assertEqual(response["temperature_c"], 28.78)

    """
        Line Noise Tests - ignore junk at head, invalid packet, junk at end, negative
    """

    def test_010_junk_head_invalid_long_scan(self):
        # expect 500 status
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/000000ce")

        self.assertEqual(ctx.exception.status, 500)

    def test_011_junk_head_invalid_long_version(self):
        # expect 500 status
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/version/rack_1/000000cf")

        self.assertEqual(ctx.exception.status, 500)

    def test_012_junk_head_invalid_long_read(self):
        # expect 500 status
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/read/thermistor/rack_1/000000cf/01ff")

        self.assertEqual(ctx.exception.status, 500)

    """
        Line Noise Tests - junk packet, no header, all negative
    """

    def test_013_junk_head_junk_scan(self):
        # expect 500 status, single thermistor
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/000000d0")

        self.assertEqual(ctx.exception.status, 500)

    def test_014_junk_head_junk_version(self):
        # expect 500 status
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/version/rack_1/000000d1")

        self.assertEqual(ctx.exception.status, 500)

    def test_015_junk_head_junk_read(self):
        # expect 500 status
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/read/thermistor/rack_1/000000d1/01ff")

        self.assertEqual(ctx.exception.status, 500)
