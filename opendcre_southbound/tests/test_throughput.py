#!/usr/bin/env python
"""
OpenDCRE Southbound API Endurance Throughput Tests
Author:  erick
Date:    9/10/2015
    \\//
     \/apor IO

Copyright (C) 2015-16  Vapor IO

This file is part of OpenDCRE.

OpenDCRE is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

OpenDCRE is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenDCRE.  If not, see <http://www.gnu.org/licenses/>.
"""
import unittest

import requests
from requests.auth import HTTPBasicAuth

from test_config import PREFIX, TEST_USERNAME, TEST_PASSWORD, SSL_CERT
from test_utils import threaded


# disable warnings for missing metadata from cert
# >> SecurityWarning: Certificate has no `subjectAltName`, falling back to check for a `commonName` for now. <<
requests.packages.urllib3.disable_warnings()

# number of threads to spawn for each test. currently, it seems that >10 threads
# causes a 502 error to be returned
THREAD_COUNT = 10


class ThroughputTestCase(unittest.TestCase):
    """
        Threaded endurance tests. Make sure there are not any lingering issues or
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
        """
            Threaded test against a scan which should return good results
        """
        @threaded(THREAD_COUNT)
        def test_scan():
            r = requests.get(PREFIX + '/scan/0000000A', verify=SSL_CERT)
            self.assertEqual(r.status_code, 200)

        test_scan()

    def test_002_bad_scan_results(self):
        """
            Threaded test against a scan which should not return good results
        """
        @threaded(THREAD_COUNT)
        def test_scan():
            r = requests.get(PREFIX + '/scan/0000000B', verify=SSL_CERT)
            self.assertEqual(r.status_code, 500)

        test_scan()

    def test_003_good_version_results(self):
        """
            Threaded test against a version request which should return good results
        """
        @threaded(THREAD_COUNT)
        def test_version():
            r = requests.get(PREFIX + '/version/0000000A', verify=SSL_CERT)
            self.assertEqual(r.status_code, 200)

        test_version()

    def test_004_bad_version_results(self):
        """
            Threaded test against a version request which should not return good results
        """
        @threaded(THREAD_COUNT)
        def test_version():
            r = requests.get(PREFIX + '/version/0000000B', verify=SSL_CERT)
            self.assertEqual(r.status_code, 500)

        test_version()

    def test_005_good_read_results(self):
        """
            Threaded test against a read request which should return good results
        """
        @threaded(THREAD_COUNT)
        def test_read_thermistor():
            r = requests.get(PREFIX + '/read/thermistor/0000000A/01FF', verify=SSL_CERT)
            self.assertEqual(r.status_code, 200)

        @threaded(THREAD_COUNT)
        def test_read_humidity():
            r = requests.get(PREFIX + '/read/humidity/0000000A/0CFF', verify=SSL_CERT)
            self.assertEqual(r.status_code, 200)

        test_read_thermistor()
        test_read_humidity()

    def test_006_bad_read_results(self):
        """
            Threaded test against a read request which should not return good results
        """
        @threaded(THREAD_COUNT)
        def test_read_thermistor():
            r = requests.get(PREFIX + '/read/thermistor/0000000B/01FF', verify=SSL_CERT)
            self.assertEqual(r.status_code, 500)

        @threaded(THREAD_COUNT)
        def test_read_humidity():
            r = requests.get(PREFIX + '/read/humidity/0000000B/0CFF', verify=SSL_CERT)
            self.assertEqual(r.status_code, 500)

        test_read_thermistor()
        test_read_humidity()

    def test_007_good_power_results(self):
        """
            Threaded test against a power status request which should return good results
        """
        @threaded(THREAD_COUNT)
        def test_power():
            r = requests.get(PREFIX+"/power/status/0000000A/02FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
            self.assertEqual(r.status_code, 200)

        test_power()

    def test_008_bad_power_results(self):
        """
            Threaded test against a power status request which should not return good results
        """
        @threaded(THREAD_COUNT)
        def test_power():
            r = requests.get(PREFIX+"/power/status/0000000B/02FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
            self.assertEqual(r.status_code, 500)

        test_power()
