#!/usr/bin/env python
""" OpenDCRE Southbound IPMI Scan Cache Registration Tests

    Author: Erick Daniszewski
    Date:   01/31/2017

    \\//
     \/apor IO

-------------------------------
Copyright (C) 2015-17  Vapor IO

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
import os
import copy
from itertools import count

import opendcre_southbound as sb

from opendcre_southbound.devicebus.devices.ipmi import IPMIDevice


class MockApp(object):
    """ Object used to mock the Flask app, specifically the flask app
    config dictionary.
    """
    def __init__(self):
        self.config = {
            'SERIAL_OVERRIDE': None,
            'HARDWARE_OVERRIDE': None,
            'COUNTER': sb._count(start=0x01, step=0x01),
            'ENDPOINT_PREFIX': '/opendcre/',
            'SCAN_CACHE': '/tmp/opendcre/cache.json',
            'DEVICES': {},
            'SINGLE_BOARD_DEVICES': {},
            'RANGE_DEVICES': [],
            'IPMI_BOARD_OFFSET': count(),
            'PLC_BOARD_OFFSET': count()
        }


class VaporTestException(Exception):
    """ Unique dummy exception raised by override method, below.
    """
    pass


def raise_err(self):
    """ Function that will be used to override parts of the IPMIDevice in order to
    ensure the correct code paths are being hit.
    """
    raise VaporTestException


class IPMIScanCacheRegistrationTestCase(unittest.TestCase):
    """ Test case for IPMI Device initialization via the scan cache.

    For reference, the OpenDCRE config used for these tests (see data/opendcre_config.json):
      {
        "scan_cache_file": "/tmp/opendcre/cache.json",
        "cache_timeout": 600,
        "cache_threshold": 500,

        "devices": {
          "ipmi": {
            "device_initializer_threads": 4,
            "scan_on_init": true,
            "from_config": "bmc_config.json"
          }
        }
      }

    and the BMC config used can be found at data/bmc_config/bmc_config005.json
    """

    @classmethod
    def setUpClass(cls):
        if not os.path.exists('/tmp/opendcre'):
            os.makedirs('/tmp/opendcre')

        cls.scan_cache = '/tmp/opendcre/cache.json'

        with open('/opendcre/opendcre_southbound/tests/data/scan_cache.json', 'r') as f:
            cls.cache_data = f.read()

        cls.device_kwargs = {
            'bmc_ip': 'ipmi-emulator-1',  # from bmc_config005.json
            'bmc_rack': 'rack_1',         # from bmc_config005.json
            'username': 'ADMIN',
            'password': 'ADMIN',
            'board_offset': 1,
            'board_id_range': (0, 100)
        }

    def tearDown(self):
        if os.path.exists(self.scan_cache):
            os.remove(self.scan_cache)

    def test_000_scan_cache_registration(self):
        """ Test initializing an IPMI device using the scan cache.

        In this case, no scan cache exists, so we expect IPMIDevice init to attempt
        the "normal" init process.
        """
        self.assertFalse(os.path.exists(self.scan_cache))

        # override the IPMIDevice method used for "normal" processing, so we know that it reached that point.
        IPMIDevice._get_board_record = raise_err

        # initialize a mock app and counter for device init
        app = MockApp()
        counter = count()

        with self.assertRaises(VaporTestException):
            IPMIDevice(app.config, counter, **self.device_kwargs)

    def test_001_scan_cache_registration(self):
        """ Test initializing an IPMI device using the scan cache.

        In this case, a scan cache exists, but the device we are initializing is not in
        it (rack_id not in cache), so we expect IPMIDevice init to attempt the "normal"
        init process.
        """
        # add the data for the scan cache
        with open(self.scan_cache, 'w') as f:
            f.write(self.cache_data)
        self.assertTrue(os.path.exists(self.scan_cache))

        # override the IPMIDevice method used for "normal" processing, so we know that it reached that point.
        IPMIDevice._get_board_record = raise_err

        # initialize a mock app and counter for device init
        app = MockApp()
        counter = count()

        # make a copy of the device kwargs and modify for this test
        kwargs = copy.deepcopy(self.device_kwargs)
        kwargs['bmc_rack'] = 'rack_99'

        with self.assertRaises(VaporTestException):
            IPMIDevice(app.config, counter, **kwargs)

    def test_002_scan_cache_registration(self):
        """ Test initializing an IPMI device using the scan cache.

        In this case, a scan cache exists, but the device we are initializing is not in
        it (bmc_ip not in cache), so we expect IPMIDevice init to attempt the "normal"
        init process.
        """
        # add the data for the scan cache
        with open(self.scan_cache, 'w') as f:
            f.write(self.cache_data)
        self.assertTrue(os.path.exists(self.scan_cache))

        # override the IPMIDevice method used for "normal" processing, so we know that it reached that point.
        IPMIDevice._get_board_record = raise_err

        # initialize a mock app and counter for device init
        app = MockApp()
        counter = count()

        # make a copy of the device kwargs and modify for this test
        kwargs = copy.deepcopy(self.device_kwargs)
        kwargs['bmc_ip'] = 'ipmi-emulator-99'

        with self.assertRaises(VaporTestException):
            IPMIDevice(app.config, counter, **kwargs)

    def test_003_scan_cache_registration(self):
        """ Test initializing an IPMI device using the scan cache.

        In this case, a scan cache exists and the device we are initializing does exist
        in the cache.
        """
        # add the data for the scan cache
        with open(self.scan_cache, 'w') as f:
            f.write(self.cache_data)
        self.assertTrue(os.path.exists(self.scan_cache))

        # override the IPMIDevice method used for "normal" processing, so we know that it reached that point.
        IPMIDevice._get_board_record = raise_err

        # initialize a mock app and counter for device init
        app = MockApp()
        counter = count()

        dev = IPMIDevice(app.config, counter, **self.device_kwargs)

        # make sure we have a IPMI device that matches the input kwargs
        self.assertIsInstance(dev, IPMIDevice)
        self.assertEqual(dev.bmc_ip, self.device_kwargs['bmc_ip'])
        self.assertEqual(dev.bmc_rack, self.device_kwargs['bmc_rack'])
        self.assertEqual(dev.username, self.device_kwargs['username'])
        self.assertEqual(dev.password, self.device_kwargs['password'])

        # make sure the ipmi device board id and board record info match that
        # of what is specified in the scan config.
        self.assertEqual(dev.board_id, 0x40000000)    # from data/scan_cache.json
        self.assertIsInstance(dev.board_record, dict)
        self.assertEqual(len(dev.board_record), 4)
        self.assertIn('board_id', dev.board_record)
        self.assertIn('ip_addresses', dev.board_record)
        self.assertIn('hostnames', dev.board_record)
        self.assertIn('devices', dev.board_record)

        self.assertIsInstance(dev.board_record['devices'], list)
        self.assertEqual(len(dev.board_record['devices']), 16)
        for device in dev.board_record['devices']:
            self.assertIsInstance(device, dict)
            self.assertIn('device_id', device)
            self.assertIn('device_info', device)
            self.assertIn('device_type', device)
