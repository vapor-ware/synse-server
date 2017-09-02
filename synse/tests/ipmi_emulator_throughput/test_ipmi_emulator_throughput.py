#!/usr/bin/env python
""" Synse IPMI Emulator Throughput Tests

    Author: Erick Daniszewski
    Date:   09/07/2016

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

import grequests as async

from synse.tests.test_config import PREFIX


class IPMIEmulatorThroughputTestCase(unittest.TestCase):
    """ Throughput tests for the IPMI emulator. These tests are used to provide an
    idea of how much traffic can be passed through to an instance of the IPMI
    emulator. This can be particularly useful when designing test setups with the
    emulator to know how many proxies a single emulator instance can support, e.g.
    against typical UI usage where there are many requests made.
    """
    # number of requests to make in total
    COUNT = 30

    # number of requests to make at a time
    SIZE = 5

    # request timeout (seconds)
    TIMEOUT = 5

    def test_001_test(self):
        """ Test hitting the 'test' endpoint of Synse in IPMI mode.
        """
        responses = []

        def _test_hook(r, **kwargs):
            responses.append(r.status_code)

        url = PREFIX + '/test'
        async.map([async.get(url, hooks={'response': [_test_hook]}, timeout=self.TIMEOUT) for _ in xrange(self.COUNT)], size=self.SIZE)

        self.assertEqual(len(responses), self.COUNT)
        for resp in responses:
            self.assertEqual(resp, 200)

    @unittest.skip('https://github.com/vapor-ware/synse-server/issues/223.')
    def test_002_test_read(self):
        """ Test reading a voltage sensor in IPMI mode.
        """
        responses = []

        def _test_hook(r, **kwargs):
            responses.append(r.status_code)

        url = PREFIX + '/read/voltage/rack_1/40000000/0021'
        async.map([async.get(url, hooks={'response': [_test_hook]}, timeout=self.TIMEOUT) for _ in xrange(self.COUNT)], size=self.SIZE)

        self.assertEqual(len(responses), self.COUNT)
        for resp in responses:
            self.assertEqual(resp, 200)

    @unittest.skip('https://github.com/vapor-ware/synse-server/issues/223.')
    def test_003_test_read(self):
        """ Test reading a fan speed sensor in IPMI mode.
        """
        responses = []

        def _test_hook(r, **kwargs):
            responses.append(r.status_code)

        url = PREFIX + '/read/fan_speed/rack_1/40000000/0042'
        async.map([async.get(url, hooks={'response': [_test_hook]}, timeout=self.TIMEOUT) for _ in xrange(self.COUNT)], size=self.SIZE)

        self.assertEqual(len(responses), self.COUNT)
        for resp in responses:
            self.assertEqual(resp, 200)

    @unittest.skip('https://github.com/vapor-ware/synse-server/issues/223.')
    def test_004_test_read(self):
        """ Test reading a temperature sensor in IPMI mode.
        """
        responses = []

        def _test_hook(r, **kwargs):
            responses.append(r.status_code)

        url = PREFIX + '/read/temperature/rack_1/40000000/0011'
        async.map([async.get(url, hooks={'response': [_test_hook]}, timeout=self.TIMEOUT) for _ in xrange(self.COUNT)], size=self.SIZE)

        self.assertEqual(len(responses), self.COUNT)
        for resp in responses:
            self.assertEqual(resp, 200)

    @unittest.skip('https://github.com/vapor-ware/synse-server/issues/223.')
    def test_005_test_power(self):
        """ Test getting power status in IPMI mode.
        """
        responses = []

        def _test_hook(r, **kwargs):
            responses.append(r.status_code)

        url = PREFIX + '/power/rack_1/40000000/0100/status'
        async.map([async.get(url, hooks={'response': [_test_hook]}, timeout=self.TIMEOUT) for _ in xrange(self.COUNT)], size=self.SIZE)

        self.assertEqual(len(responses), self.COUNT)
        for resp in responses:
            self.assertEqual(resp, 200)

    @unittest.skip('https://github.com/vapor-ware/synse-server/issues/223.')
    def test_006_test_power(self):
        """ Test power control (off) in IPMI mode.
        """
        responses = []

        def _test_hook(r, **kwargs):
            responses.append(r.status_code)

        url = PREFIX + '/power/rack_1/40000000/0100/off'
        async.map([async.get(url, hooks={'response': [_test_hook]}, timeout=self.TIMEOUT) for _ in xrange(self.COUNT)], size=self.SIZE)

        self.assertEqual(len(responses), self.COUNT)
        for resp in responses:
            self.assertEqual(resp, 200)

    @unittest.skip('https://github.com/vapor-ware/synse-server/issues/223.')
    def test_007_test_power(self):
        """ Test power control (on) in IPMI mode.
        """
        responses = []

        def _test_hook(r, **kwargs):
            responses.append(r.status_code)

        url = PREFIX + '/power/rack_1/40000000/0100/on'
        async.map([async.get(url, hooks={'response': [_test_hook]}, timeout=self.TIMEOUT) for _ in xrange(self.COUNT)], size=self.SIZE)

        self.assertEqual(len(responses), self.COUNT)
        for resp in responses:
            self.assertEqual(resp, 200)

    @unittest.skip('https://github.com/vapor-ware/synse-server/issues/223.')
    def test_008_test_asset_info(self):
        """ Test getting asset info in IPMI mode.
        """
        responses = []

        def _test_hook(r, **kwargs):
            responses.append(r.status_code)

        url = PREFIX + '/asset/rack_1/40000000/0200'
        async.map([async.get(url, hooks={'response': [_test_hook]}, timeout=self.TIMEOUT) for _ in xrange(self.COUNT)], size=self.SIZE)

        self.assertEqual(len(responses), self.COUNT)
        for resp in responses:
            self.assertEqual(resp, 200)

    @unittest.skip('https://github.com/vapor-ware/synse-server/issues/223.')
    def test_009_test_boot_target(self):
        """ Test getting boot target info in IPMI mode.
        """
        responses = []

        def _test_hook(r, **kwargs):
            responses.append(r.status_code)

        url = PREFIX + '/boot_target/rack_1/40000000/0200'
        async.map([async.get(url, hooks={'response': [_test_hook]}, timeout=self.TIMEOUT) for _ in xrange(self.COUNT)], size=self.SIZE)

        self.assertEqual(len(responses), self.COUNT)
        for resp in responses:
            self.assertEqual(resp, 200)

    @unittest.skip('https://github.com/vapor-ware/synse-server/issues/223.')
    def test_010_test_boot_target(self):
        """ Test setting boot target info in IPMI mode.
        """
        responses = []

        def _test_hook(r, **kwargs):
            responses.append(r.status_code)

        url = PREFIX + '/boot_target/rack_1/40000000/0200/pxe'
        async.map([async.get(url, hooks={'response': [_test_hook]}, timeout=self.TIMEOUT) for _ in xrange(self.COUNT)], size=self.SIZE)

        self.assertEqual(len(responses), self.COUNT)
        for resp in responses:
            self.assertEqual(resp, 200)

    @unittest.skip('https://github.com/vapor-ware/synse-server/issues/223.')
    def test_011_test_boot_target(self):
        """ Test setting boot target info in IPMI mode.
        """
        responses = []

        def _test_hook(r, **kwargs):
            responses.append(r.status_code)

        url = PREFIX + '/boot_target/rack_1/40000000/0200/hdd'
        async.map([async.get(url, hooks={'response': [_test_hook]}, timeout=self.TIMEOUT) for _ in xrange(self.COUNT)], size=self.SIZE)

        self.assertEqual(len(responses), self.COUNT)
        for resp in responses:
            self.assertEqual(resp, 200)

    @unittest.skip('https://github.com/vapor-ware/synse-server/issues/223.')
    def test_012_test_location(self):
        """ Test getting location info in IPMI mode.
        """
        responses = []

        def _test_hook(r, **kwargs):
            responses.append(r.status_code)

        url = PREFIX + '/location/rack_1/40000000'
        async.map([async.get(url, hooks={'response': [_test_hook]}, timeout=self.TIMEOUT) for _ in xrange(self.COUNT)], size=self.SIZE)

        self.assertEqual(len(responses), self.COUNT)
        for resp in responses:
            self.assertEqual(resp, 200)

    @unittest.skip('https://github.com/vapor-ware/synse-server/issues/223.')
    def test_013_test_led(self):
        """ Test getting led state in IPMI mode.
        """
        responses = []

        def _test_hook(r, **kwargs):
            responses.append(r.status_code)

        url = PREFIX + '/led/rack_1/40000000/0300'
        async.map([async.get(url, hooks={'response': [_test_hook]}, timeout=self.TIMEOUT) for _ in xrange(self.COUNT)], size=self.SIZE)

        self.assertEqual(len(responses), self.COUNT)
        for resp in responses:
            self.assertEqual(resp, 200)

    @unittest.skip('https://github.com/vapor-ware/synse-server/issues/223.')
    def test_014_test_led(self):
        """ Test setting led state (on) in IPMI mode.
        """
        responses = []

        def _test_hook(r, **kwargs):
            responses.append(r.status_code)

        url = PREFIX + '/led/rack_1/40000000/0300/on'
        async.map([async.get(url, hooks={'response': [_test_hook]}, timeout=self.TIMEOUT) for _ in xrange(self.COUNT)], size=self.SIZE)

        self.assertEqual(len(responses), self.COUNT)
        for resp in responses:
            self.assertEqual(resp, 200)

    @unittest.skip('https://github.com/vapor-ware/synse-server/issues/223.')
    def test_015_test_led(self):
        """ Test setting led state (off) in IPMI mode.
        """
        responses = []

        def _test_hook(r, **kwargs):
            responses.append(r.status_code)

        url = PREFIX + '/led/rack_1/40000000/0300/off'
        async.map([async.get(url, hooks={'response': [_test_hook]}, timeout=self.TIMEOUT) for _ in xrange(self.COUNT)], size=self.SIZE)

        self.assertEqual(len(responses), self.COUNT)
        for resp in responses:
            self.assertEqual(resp, 200)

    @unittest.skip('https://github.com/vapor-ware/synse-server/issues/223.')
    def test_015_test_fan(self):
        """ Test getting fan speed in IPMI mode.
        """
        responses = []

        def _test_hook(r, **kwargs):
            responses.append(r.status_code)

        url = PREFIX + '/fan/rack_1/40000000/0042'
        async.map([async.get(url, hooks={'response': [_test_hook]}, timeout=self.TIMEOUT) for _ in xrange(self.COUNT)], size=self.SIZE)

        self.assertEqual(len(responses), self.COUNT)
        for resp in responses:
            self.assertEqual(resp, 200)

    @unittest.skip('https://github.com/vapor-ware/synse-server/issues/223.')
    def test_016_test_host_info(self):
        """ Test getting host info in IPMI mode.
        """
        responses = []

        def _test_hook(r, **kwargs):
            responses.append(r.status_code)

        url = PREFIX + '/host_info/rack_1/40000000/0100'
        async.map([async.get(url, hooks={'response': [_test_hook]}, timeout=self.TIMEOUT) for _ in xrange(self.COUNT)], size=self.SIZE)

        self.assertEqual(len(responses), self.COUNT)
        for resp in responses:
            self.assertEqual(resp, 200)

    @unittest.skip('https://github.com/vapor-ware/synse-server/issues/223.')
    def test_017_test_scan_all(self):
        """ Test issuing a scan all command in IPMI mode.
        """
        responses = []

        def _test_hook(r, **kwargs):
            responses.append(r.status_code)

        url = PREFIX + '/scan'
        async.map([async.get(url, hooks={'response': [_test_hook]}, timeout=self.TIMEOUT) for _ in xrange(self.COUNT)], size=self.SIZE)

        self.assertEqual(len(responses), self.COUNT)
        for resp in responses:
            self.assertEqual(resp, 200)

    @unittest.skip('https://github.com/vapor-ware/synse-server/issues/223.')
    def test_018_test_scan_all(self):
        """ Test issuing a force scan all command in IPMI mode.
        """
        responses = []

        def _test_hook(r, **kwargs):
            responses.append(r.status_code)

        url = PREFIX + '/scan/force'
        async.map([async.get(url, hooks={'response': [_test_hook]}, timeout=self.TIMEOUT) for _ in xrange(self.COUNT)], size=self.SIZE)

        self.assertEqual(len(responses), self.COUNT)
        for resp in responses:
            self.assertEqual(resp, 200)

    @unittest.skip('https://github.com/vapor-ware/synse-server/issues/223.')
    def test_019_test_scan(self):
        """ Test scanning a rack in IPMI mode.
        """
        responses = []

        def _test_hook(r, **kwargs):
            responses.append(r.status_code)

        url = PREFIX + '/scan/rack_1'
        async.map([async.get(url, hooks={'response': [_test_hook]}, timeout=self.TIMEOUT) for _ in xrange(self.COUNT)], size=self.SIZE)

        self.assertEqual(len(responses), self.COUNT)
        for resp in responses:
            self.assertEqual(resp, 200)

    @unittest.skip('https://github.com/vapor-ware/synse-server/issues/223.')
    def test_020_test_scan(self):
        """ Test scanning a board in IPMI mode.
        """
        responses = []

        def _test_hook(r, **kwargs):
            responses.append(r.status_code)

        url = PREFIX + '/scan/rack_1/40000000'
        async.map([async.get(url, hooks={'response': [_test_hook]}, timeout=self.TIMEOUT) for _ in xrange(self.COUNT)], size=self.SIZE)

        self.assertEqual(len(responses), self.COUNT)
        for resp in responses:
            self.assertEqual(resp, 200)
