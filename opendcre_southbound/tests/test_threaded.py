#!/usr/bin/env python
"""
OpenDCRE Southbound API Threaded Endurance Tests
Author:  erick
Date:    9/9/2015
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
import json

import requests
from requests.auth import HTTPBasicAuth

from test_config import PREFIX, TEST_USERNAME, TEST_PASSWORD, SSL_CERT
from test_utils import TestThreadExecutor


# disable warnings for missing metadata from cert
# >> SecurityWarning: Certificate has no `subjectAltName`, falling back to check for a `commonName` for now. <<
requests.packages.urllib3.disable_warnings()

# number of threads for each test
THREAD_COUNT = 25


class ThreadedTestCase(unittest.TestCase):
    """
        Threaded endurance tests. Make sure there are not any lingering issues or
        clogged pipes between the bus and flask.

        FIXME: there is something kind of strange going on with these tests, where they
        either take ~1 second to complete or ~13 seconds (on my machine). unclear as to
        why it takes so long for some tests.

        The threaded test cases do not run daemonized threads (see throughput tests), but
        instead, each of the tests contained in this test case join their test threads prior
        to test completion. in this way, only one kind of call is being made (read, version, ..)
        at a time, though many calls of that type are being made. This is not necessarily ideal,
        however the 'callback' which checks a thread's resolution state requires this setup to
        work, at least for now.
    """
    def test_001_good_scan_results(self):
        """
            Threaded test against a scan which should return good results
        """
        def test_scan():
            r = requests.get(PREFIX + '/scan/0000000A', verify=SSL_CERT)
            self.assertEqual(r.status_code, 200)
            response = json.loads(r.text)
            self.assertEqual(len(response['boards']), 1)
            self.assertEqual(len(response['boards'][0]['devices']), 3)

        executor = TestThreadExecutor(THREAD_COUNT, test_scan)
        results = executor.execute()
        for result in results:
            self.assertEqual(result, True)

    def test_002_bad_scan_results(self):
        """
            Threaded test against a scan which should not return good results
        """
        def test_scan():
            r = requests.get(PREFIX + '/scan/0000000B', verify=SSL_CERT)
            self.assertEqual(r.status_code, 500)

        executor = TestThreadExecutor(THREAD_COUNT, test_scan)
        results = executor.execute()
        for result in results:
            self.assertEqual(result, True)

    def test_003_good_version_results(self):
        """
            Threaded test against a version request which should return good results
        """
        def test_version():
            r = requests.get(PREFIX + '/version/0000000A', verify=SSL_CERT)
            self.assertEqual(r.status_code, 200)
            response = json.loads(r.text)
            self.assertEqual(response['firmware_version'], 'Version Response 1')

        executor = TestThreadExecutor(THREAD_COUNT, test_version)
        results = executor.execute()
        for result in results:
            self.assertEqual(result, True)

    def test_004_bad_version_results(self):
        """
            Threaded test against a version request which should not return good results
        """
        def test_version():
            r = requests.get(PREFIX + '/version/0000000B', verify=SSL_CERT)
            self.assertEqual(r.status_code, 500)

        executor = TestThreadExecutor(THREAD_COUNT, test_version)
        results = executor.execute()
        for result in results:
            self.assertEqual(result, True)

    def test_005_good_read_results(self):
        """
            Threaded test against a read request which should return good results
        """
        def test_read_thermistor():
            r = requests.get(PREFIX + '/read/thermistor/0000000A/01FF', verify=SSL_CERT)
            self.assertEqual(r.status_code, 200)
            response = json.loads(r.text)
            # self.assertEqual(response['device_raw'], 656)
            self.assertAlmostEqual(response['temperature_c'], 28.7, delta=0.1)

        def test_read_humidity():
            r = requests.get(PREFIX + '/read/humidity/0000000A/0CFF', verify=SSL_CERT)
            self.assertEqual(r.status_code, 200)
            response = json.loads(r.text)
            # self.assertEqual(response['device_raw'], 1486313281)
            self.assertEqual(response['temperature_c'], 16.24)
            self.assertEqual(response['humidity'], 38.43)

        executor = TestThreadExecutor(THREAD_COUNT, test_read_thermistor)
        results = executor.execute()
        for result in results:
            self.assertEqual(result, True)

        executor = TestThreadExecutor(THREAD_COUNT, test_read_humidity)
        results = executor.execute()
        for result in results:
            self.assertEqual(result, True)

    def test_006_bad_read_results(self):
        """
            Threaded test against a read request which should not return good results
        """
        def test_read_thermistor():
            r = requests.get(PREFIX + '/read/thermistor/0000000B/01FF', verify=SSL_CERT)
            self.assertEqual(r.status_code, 500)

        def test_read_humidity():
            r = requests.get(PREFIX + '/read/humidity/0000000B/0CFF', verify=SSL_CERT)
            self.assertEqual(r.status_code, 500)

        executor = TestThreadExecutor(THREAD_COUNT, test_read_thermistor)
        results = executor.execute()
        for result in results:
            self.assertEqual(result, True)

        executor = TestThreadExecutor(THREAD_COUNT, test_read_humidity)
        results = executor.execute()
        for result in results:
            self.assertEqual(result, True)

    def test_007_good_multi_read_results(self):
        """
            Threaded test against reading from different devices which should return good results
        """
        def test_read():
            # thermistor request
            r = requests.get(PREFIX + '/read/thermistor/0000000A/01FF', verify=SSL_CERT)
            self.assertEqual(r.status_code, 200)
            response = json.loads(r.text)
            # self.assertEqual(response['device_raw'], 656)
            self.assertAlmostEqual(response['temperature_c'], 28.7, delta=0.1)

            # humidity request
            r = requests.get(PREFIX + '/read/humidity/0000000A/0CFF', verify=SSL_CERT)
            self.assertEqual(r.status_code, 200)
            response = json.loads(r.text)
            # self.assertEqual(response['device_raw'], 1486313281)
            self.assertEqual(response['temperature_c'], 16.24)
            self.assertEqual(response['humidity'], 38.43)

        executor = TestThreadExecutor(THREAD_COUNT, test_read)
        results = executor.execute()
        for result in results:
            self.assertEqual(result, True)

    def test_008_bad_multi_read_results(self):
        """
            Threaded test against reading from different devices which should not return good results
        """
        def test_read():
            # thermistor request
            r = requests.get(PREFIX + '/read/thermistor/0000000B/01FF', verify=SSL_CERT)
            self.assertEqual(r.status_code, 500)

            # humidity request
            r = requests.get(PREFIX + '/read/humidity/0000000B/0CFF', verify=SSL_CERT)
            self.assertEqual(r.status_code, 500)

        executor = TestThreadExecutor(THREAD_COUNT, test_read)
        results = executor.execute()
        for result in results:
            self.assertEqual(result, True)

    def test_009_good_power_results(self):
        """
            Threaded test against a power status request which should return good results
        """
        def test_power():
            r = requests.get(PREFIX+"/power/status/0000000A/02FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
            self.assertEqual(r.status_code, 200)
            response = json.loads(r.text)
            self.assertEqual(response["pmbus_raw"], "64,0,0,0")
            self.assertEqual(response["power_status"], "off")
            self.assertEqual(response["power_ok"], True)
            self.assertEqual(response["over_current"], False)
            self.assertEqual(response["under_voltage"], False)

        executor = TestThreadExecutor(THREAD_COUNT, test_power)
        results = executor.execute()
        for result in results:
            self.assertEqual(result, True)

    def test_010_bad_power_results(self):
        """
            Threaded test against a power status request which should not return good results
        """
        def test_power():
            r = requests.get(PREFIX+"/power/status/0000000B/02FF", auth=HTTPBasicAuth(TEST_USERNAME, TEST_PASSWORD), verify=SSL_CERT)
            self.assertEqual(r.status_code, 500)

        executor = TestThreadExecutor(THREAD_COUNT, test_power)
        results = executor.execute()
        for result in results:
            self.assertEqual(result, True)
