#!/usr/bin/env python
""" Synse API Endurance Tests

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
import random
import unittest

from vapor_common import http

from synse.tests.test_config import PREFIX


class EnduranceTestCase(unittest.TestCase):
    """ Basic endurance tests.  Make sure there are not any lingering issues or
    clogged pipes between the bus and flask.
    """

    def test_001_random_good_http(self):
        request_urls = [
            PREFIX + '/scan/rack_1/00000001',
            PREFIX + '/version/rack_1/00000001',
            PREFIX + '/read/thermistor/rack_1/00000001/01FF',
            PREFIX + '/read/humidity/rack_1/00000001/0CFF'
        ]
        for x in range(100):
            r = http.get(request_urls[random.randint(0, len(request_urls) - 1)])
            self.assertTrue(http.request_ok(r.status_code))

    def test_002_device_reads(self):
        for x in range(100):
            r = http.get(PREFIX + '/read/thermistor/rack_1/00000001/01FF')
            self.assertTrue(http.request_ok(r.status_code))

            r = http.get(PREFIX + '/read/humidity/rack_1/00000001/0CFF')
            self.assertTrue(http.request_ok(r.status_code))
