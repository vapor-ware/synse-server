#!/usr/bin/env python
""" Synse API Endurance Throughput Tests

    Author:  Erick Daniszewski
    Date:    9/10/2015

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

from synse.tests.test_config import PREFIX
from synse.tests.test_utils import threaded
from synse.vapor_common import http
from synse.vapor_common.errors import VaporHTTPError

# number of threads to spawn for each test. currently, it seems that >10 threads
# causes a 502 error to be returned
THREAD_COUNT = 10


class ThroughputTestCase(unittest.TestCase):
    """ Threaded endurance tests. Make sure there are not any lingering issues or
    clogged pipes between the bus and flask.

    FIXME: the @threaded decorator spawns up a bunch of daemon threads. the problem
    here is that threads do not communicate back to the main thread which is actually
    running the unittest. so, even if exceptions are thrown on the spawned threads,
    the test case will pass since its main thread is unaware of the spawned threads'
    failures. this should either be fixed somehow, or it should be acknowledged that
    this test is only valuable when viewing the output, since exceptions in threads
    will be written to stdout (or to a logfile, eventually).
    """

    def test_001_good_scan_results(self):
        """ Threaded test against a scan which should return good results
        """

        @threaded(THREAD_COUNT)
        def test_scan():
            r = http.get(PREFIX + '/scan/rack_1/0000000A')
            self.assertTrue(http.request_ok(r.status_code))

        test_scan()

    def test_002_bad_scan_results(self):
        """ Threaded test against a scan which should not return good results
        """

        @threaded(THREAD_COUNT)
        def test_scan():
            with self.assertRaises(VaporHTTPError) as ctx:
                http.get(PREFIX + '/scan/rack_1/0000000B')

            self.assertEqual(ctx.exception.status, 500)

        test_scan()

    def test_003_good_version_results(self):
        """ Threaded test against a version request which should return good results
        """

        @threaded(THREAD_COUNT)
        def test_version():
            r = http.get(PREFIX + '/version/0000000A')
            self.assertTrue(http.request_ok(r.status_code))

        test_version()

    def test_004_bad_version_results(self):
        """ Threaded test against a version request which should not return good results
        """

        @threaded(THREAD_COUNT)
        def test_version():
            with self.assertRaises(VaporHTTPError) as ctx:
                http.get(PREFIX + '/version/0000000B')

            self.assertEqual(ctx.exception.status, 500)

        test_version()

    def test_005_good_read_results(self):
        """ Threaded test against a read request which should return good results
        """

        @threaded(THREAD_COUNT)
        def test_read_thermistor():
            r = http.get(PREFIX + '/read/rack_1/thermistor/0000000A/01FF')
            self.assertTrue(http.request_ok(r.status_code))

        @threaded(THREAD_COUNT)
        def test_read_humidity():
            r = http.get(PREFIX + '/read/rack_1/humidity/0000000A/0CFF')
            self.assertTrue(http.request_ok(r.status_code))

        test_read_thermistor()
        test_read_humidity()

    def test_006_bad_read_results(self):
        """ Threaded test against a read request which should not return good results
        """

        @threaded(THREAD_COUNT)
        def test_read_thermistor():
            with self.assertRaises(VaporHTTPError) as ctx:
                http.get(PREFIX + '/read/rack_1/thermistor/0000000B/01FF')

            self.assertEqual(ctx.exception.status, 500)

        @threaded(THREAD_COUNT)
        def test_read_humidity():
            with self.assertRaises(VaporHTTPError) as ctx:
                http.get(PREFIX + '/read/rack_1/humidity/0000000B/0CFF')

            self.assertEqual(ctx.exception.status, 500)

        test_read_thermistor()
        test_read_humidity()

    def test_007_good_power_results(self):
        """ Threaded test against a power status request which should return good results
        """

        @threaded(THREAD_COUNT)
        def test_power():
            r = http.get(PREFIX + '/power/status/0000000A/02FF')
            self.assertTrue(http.request_ok(r.status_code))

        test_power()

    def test_008_bad_power_results(self):
        """ Threaded test against a power status request which should not return good results
        """

        @threaded(THREAD_COUNT)
        def test_power():
            with self.assertRaises(VaporHTTPError) as ctx:
                http.get(PREFIX + '/power/status/0000000B/02FF')

            self.assertEqual(ctx.exception.status, 500)

        test_power()
