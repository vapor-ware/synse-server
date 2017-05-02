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

    def test_001_junk_head_scan(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/000000c8")

        self.assertEqual(ctx.exception.status, 500)
        self.assertIn('not associated with any registered devicebus handler', ctx.exception.json['message'])

    def test_004_junk_head_tooshort_scan(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/000000ca")

        self.assertEqual(ctx.exception.status, 500)
        self.assertIn('not associated with any registered devicebus handler', ctx.exception.json['message'])

    def test_007_junk_head_valid_long_scan(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/000000cc")

        self.assertEqual(ctx.exception.status, 500)
        self.assertIn('not associated with any registered devicebus handler', ctx.exception.json['message'])

    def test_010_junk_head_invalid_long_scan(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/000000ce")

        self.assertEqual(ctx.exception.status, 500)
        self.assertIn('not associated with any registered devicebus handler', ctx.exception.json['message'])

    def test_013_junk_head_junk_scan(self):
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/rack_1/000000d0")

        self.assertEqual(ctx.exception.status, 500)
        self.assertIn('not associated with any registered devicebus handler', ctx.exception.json['message'])
