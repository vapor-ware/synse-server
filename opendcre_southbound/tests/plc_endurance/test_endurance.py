#!/usr/bin/env python
""" VaporCORE Southbound API Endurance Tests

    Author:  andrew
    Date:    4/13/2015

    \\//
     \/apor IO
"""
import random
import unittest

from opendcre_southbound.tests.test_config import PREFIX
from vapor_common import http


class EnduranceTestCase(unittest.TestCase):
    """ Basic endurance tests.  Make sure there are not any lingering issues or
    clogged pipes between the bus and flask.
    """

    def test_001_random_good_http(self):
        request_urls = [
            PREFIX + "/scan/rack_1/00000001",
            PREFIX + "/version/rack_1/00000001",
            PREFIX + "/read/thermistor/rack_1/00000001/01FF",
            PREFIX + "/read/humidity/rack_1/00000001/0CFF"
        ]
        for x in range(100):
            r = http.get(request_urls[random.randint(0, len(request_urls) - 1)])
            self.assertTrue(http.request_ok(r.status_code))

    def test_002_device_reads(self):
        for x in range(100):
            r = http.get(PREFIX + "/read/thermistor/rack_1/00000001/01FF")
            self.assertTrue(http.request_ok(r.status_code))

            r = http.get(PREFIX + "/read/humidity/rack_1/00000001/0CFF")
            self.assertTrue(http.request_ok(r.status_code))
