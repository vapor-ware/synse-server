#!/usr/bin/env python
""" VaporCORE Southbound API Scan-all Protocol Tests

    Author:  andrew
    Date:    2/28/2016

    \\//
     \/apor IO
"""
import unittest

from opendcre_southbound.tests.test_config import PREFIX
from vapor_common import http
from vapor_common.errors import VaporHTTPError


class ScanAllTestCase(unittest.TestCase):
    """ Test board scan all, with various results.
    """

    def test_001_scan_all_ok(self):
        """ Test expecting ok results (10 boards)
        """
        r = http.get(PREFIX + "/scan/force")
        response = r.json()
        self.assertTrue(http.request_ok(r.status_code))
        self.assertEqual(len(response['racks'][0]["boards"]), 10)

    '''
    def test_002_scan_all_fail(self):
        """ Test expecting failed results (error, error, error --> 500)
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/force")

        self.assertEqual(ctx.exception.status, 500)
        print ctx.exception.json

    def test_003_scan_all_two_bad_ok(self):
        """ Test expecting ok results (10 boards)
        """
        r = http.get(PREFIX + "/scan/force")
        response = r.json()
        self.assertEqual(len(response['racks'][0]["boards"]), 10)
        self.assertTrue(http.request_ok(r.status_code))

    def test_004_scan_all_one_bad_ok(self):
        """ Test expecting ok results (10 boards)
        """
        r = http.get(PREFIX + "/scan/force")
        response = r.json()
        self.assertEqual(len(response['racks'][0]['boards']), 10)
        self.assertTrue(http.request_ok(r.status_code))

    def test_005_scan_all_error_then_read(self):
        """ Test expecting failed results (error, error, error --> 500)
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/force")

        self.assertEqual(ctx.exception.status, 500)
        print ctx.exception.json

        r = http.get(PREFIX + "/read/temperature/rack_1/00000002/2000")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(response['temperature_c'], 28.78)

    def test_006_scan_all_error_then_scan_board(self):
        """ Test expecting failed results (error, error, error --> 500)
        """
        with self.assertRaises(VaporHTTPError) as ctx:
            http.get(PREFIX + "/scan/force")

        self.assertEqual(ctx.exception.status, 500)
        print ctx.exception.json

        r = http.get(PREFIX + "/scan/rack_1/00000001")
        self.assertTrue(http.request_ok(r.status_code))
        response = r.json()
        self.assertEqual(len(response["boards"]), 1)
        self.assertEqual(len(response["boards"][0]['devices']), 2)
    '''
