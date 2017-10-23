#!/usr/bin/env python
""" Synse API Endpoint Utils and Helpers test case

    Author:  Erick Daniszewski
    Date:    10/12/2016

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
import uuid
from itertools import count

import synse.app as sb
from synse.devicebus.devices import IPMIDevice, PLCDevice, RedfishDevice
from synse.errors import SynseException


class MockApp(object):
    """ Object used to mock the Flask app, specifically the flask app
    config dictionary.
    """
    def __init__(self):
        self.config = {
            'SERIAL_OVERRIDE': None,
            'HARDWARE_OVERRIDE': None,
            'COUNTER': sb._count(start=0x01, step=0x01),
            'ENDPOINT_PREFIX': '/synse/',
            'SCAN_CACHE': '/tmp/synse/cache.json',
            'DEVICES': {},
            'SINGLE_BOARD_DEVICES': {},
            'IPMI_BOARD_OFFSET': count(),
            'I2C_BOARD_OFFSET': count(),
            'RS485_BOARD_OFFSET': count(),
            'PLC_BOARD_OFFSET': count(),
            'REDFISH_BOARD_OFFSET': count()
        }


class EndpointUtilitiesTestCase(unittest.TestCase):
    """ Tests for the utility and helper methods used in the setup and operation
    of the synse endpoint.
    """
    @classmethod
    def setUpClass(cls):

        cls.sample_plc_device = {
            'device_name': '/dev/ttyVapor002',
            'hardware_type': 'emulator',
            'lockfile': '/tmp/test-lock',
            'timeout': 0.25,
            'bps': 115200,
            'board_id_range': (0x00000000, 0x3fffffff),
            'board_id_range_max': 0x3fffffff,
            'board_id_range_min': 0x00000000
        }

        cls.sample_ipmi_device = {
            'bmc_ip': 'ipmi-emulator-x64',
            'bmc_port': 623,
            'username': 'ADMIN',
            'password': 'ADMIN',
            'hostnames': ['test-00'],
            'ip_addresses': ['192.168.0.100'],
            'bmc_rack': 'rack-1',
            'board_offset': 20,
            'board_id_range': (0x40000000, 0x4fffffff)
        }

        cls.sample_redfish_device = {
            'redfish_ip': 'redfish-emulator-x64',
            'redfish_port': 5040,
            'username': 'root',
            'password': 'redfish',
            'hostnames': ['127.0.0.1'],
            'ip_addresses': ['127.0.0.1'],
            'server_rack': 'rack-1',
            'board_offset': 10,
            'board_id_range': (0x70000000, 0x7fffffff)
        }

    def test_000_count(self):
        """ Test that the count generator does not exceed 0xff.
        """
        _count = sb._count()

        for _ in xrange(0x200):
            self.assertLess(next(_count), 0xff)

    def test_001_register_plc(self):
        """ Test registering a single PLC device.
        """
        # define the PLC config
        plc_devices = {
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'lockfile': '/tmp/test-lock',
                        'hardware_type': 'emulator',
                        'devices': [
                            {
                                'device_name': '/dev/ttyVapor002',
                                'retry_limit': 3,
                                'timeout': 0.25,
                                'time_slice': 75,
                                'bps': 115200
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the plc device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the plc device(s)
        PLCDevice.register(
            devicebus_config=plc_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # now check that the starting state has been mutated to include
        # the newly registered device(s)
        devices = app.config['DEVICES']
        self.assertIsInstance(devices, dict)
        self.assertEqual(len(devices), len(plc_devices['config']['racks'][0]['devices']))
        for uid, device in devices.iteritems():
            self.assertIsInstance(uid, uuid.UUID)
            self.assertIsInstance(device, PLCDevice)

        # the PLC emulator uses a config with 4 boards, so we should expect 4 items
        # in the lookup table.
        single_board_devices = app.config['SINGLE_BOARD_DEVICES']
        self.assertIsInstance(single_board_devices, dict)
        self.assertEqual(len(single_board_devices), 4)
        for item in single_board_devices.values():
            self.assertIsInstance(item, PLCDevice)

    def test_002_register_plc(self):
        """ Test registering multiple PLC devices.
        """
        # define the PLC config
        plc_devices = {
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'lockfile': '/tmp/test-lock',
                        'hardware_type': 'emulator',
                        'devices': [
                            {
                                'device_name': '/dev/ttyVapor002',
                                'retry_limit': 3,
                                'timeout': 0.25,
                                'time_slice': 75,
                                'bps': 115200
                            },
                            {
                                'device_name': '/dev/ttyVapor002',
                                'retry_limit': 3,
                                'timeout': 0.25,
                                'time_slice': 75,
                                'bps': 115200
                            },
                            {
                                'device_name': '/dev/ttyVapor002',
                                'retry_limit': 3,
                                'timeout': 0.25,
                                'time_slice': 75,
                                'bps': 115200
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the plc device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the plc device(s)
        PLCDevice.register(
            devicebus_config=plc_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # now check that the starting state has been mutated to include
        # the newly registered device(s)
        devices = app.config['DEVICES']
        self.assertIsInstance(devices, dict)
        self.assertEqual(len(devices), len(plc_devices['config']['racks'][0]['devices']))
        for uid, device in devices.iteritems():
            self.assertIsInstance(uid, uuid.UUID)
            self.assertIsInstance(device, PLCDevice)

        # we will still get only 4 devices populated here, even though we are
        # scanning more than 1 bus. this is because we are scanning the same
        # bus multiple times, and the board IDs will be the same for each scan
        single_board_devices = app.config['SINGLE_BOARD_DEVICES']
        self.assertIsInstance(single_board_devices, dict)
        self.assertEqual(len(single_board_devices), 4)
        for item in single_board_devices.values():
            self.assertIsInstance(item, PLCDevice)

    def test_003_register_plc(self):
        """ Test registering no PLC devices.
        """
        # define the PLC config
        plc_devices = {}

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the plc device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the plc device(s)
        PLCDevice.register(
            devicebus_config=plc_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # verify that nothing changed
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

    def test_004_register_plc(self):
        """ Test registering a single PLC device when other config already
        exists in the app config.
        """
        # define the PLC config
        plc_devices = {
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'lockfile': '/tmp/test-lock',
                        'hardware_type': 'emulator',
                        'devices': [
                            {
                                'device_name': '/dev/ttyVapor002',
                                'retry_limit': 3,
                                'timeout': 0.25,
                                'time_slice': 75,
                                'bps': 115200
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()

        _plc_device = PLCDevice(
            counter=app.config['COUNTER'],
            **self.sample_plc_device
        )

        app.config['DEVICES'] = {uuid.uuid4(): _plc_device}
        app.config['SINGLE_BOARD_DEVICES'] = {}

        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the plc device(s)
        self.assertEqual(len(app.config['DEVICES']), 1)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the plc device(s)
        PLCDevice.register(
            devicebus_config=plc_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # now check that the starting state has been mutated to include
        # the newly registered device(s)
        devices = app.config['DEVICES']
        self.assertIsInstance(devices, dict)
        self.assertEqual(len(devices), len(plc_devices['config']['racks'][0]['devices']) + 1)
        for uid, device in devices.iteritems():
            self.assertIsInstance(uid, uuid.UUID)
            self.assertIsInstance(device, PLCDevice)

        # the PLC emulator uses a config with 4 boards, so we should expect 4 items
        # in the lookup table.
        single_board_devices = app.config['SINGLE_BOARD_DEVICES']
        self.assertIsInstance(single_board_devices, dict)
        self.assertEqual(len(single_board_devices), 4)
        for item in single_board_devices.values():
            self.assertIsInstance(item, PLCDevice)

    def test_005_register_plc(self):
        """ Test registering multiple PLC devices when other config already
        exists in the app config.
        """
        # define the PLC config
        plc_devices = {
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'lockfile': '/tmp/test-lock',
                        'hardware_type': 'emulator',
                        'devices': [
                            {
                                'device_name': '/dev/ttyVapor002',
                                'retry_limit': 3,
                                'timeout': 0.25,
                                'time_slice': 75,
                                'bps': 115200
                            },
                            {
                                'device_name': '/dev/ttyVapor002',
                                'retry_limit': 3,
                                'timeout': 0.25,
                                'time_slice': 75,
                                'bps': 115200
                            },
                            {
                                'device_name': '/dev/ttyVapor002',
                                'retry_limit': 3,
                                'timeout': 0.25,
                                'time_slice': 75,
                                'bps': 115200
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()

        _plc_device = PLCDevice(
            counter=app.config['COUNTER'],
            **self.sample_plc_device
        )

        app.config['DEVICES'] = {uuid.uuid4(): _plc_device}
        app.config['SINGLE_BOARD_DEVICES'] = {}

        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the plc device(s)
        self.assertEqual(len(app.config['DEVICES']), 1)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the plc device(s)
        PLCDevice.register(
            devicebus_config=plc_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # now check that the starting state has been mutated to include
        # the newly registered device(s)
        devices = app.config['DEVICES']
        self.assertIsInstance(devices, dict)
        self.assertEqual(len(devices), len(plc_devices['config']['racks'][0]['devices']) + 1)
        for uid, device in devices.iteritems():
            self.assertIsInstance(uid, uuid.UUID)
            self.assertIsInstance(device, PLCDevice)

        # we will get only 4 devices populated here, even though we are
        # scanning more than 1 bus. this is because we are scanning the same
        # bus multiple times, and the board IDs will be the same for each scan
        single_board_devices = app.config['SINGLE_BOARD_DEVICES']
        self.assertIsInstance(single_board_devices, dict)
        self.assertEqual(len(single_board_devices), 4)
        for item in single_board_devices.values():
            self.assertIsInstance(item, PLCDevice)

    def test_006_register_plc(self):
        """ Test registering a single PLC device when a value is missing from
        the incoming config.
        """
        # define the PLC config
        plc_devices = {
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'lockfile': '/tmp/test-lock',
                        'hardware_type': 'emulator',
                        'devices': [
                            {
                                'retry_limit': 3,
                                'timeout': 0.25,
                                'time_slice': 75,
                                'bps': 115200
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the plc device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        with self.assertRaises(KeyError):
            # register the plc device(s)
            PLCDevice.register(
                devicebus_config=plc_devices,
                app_config=app.config,
                app_cache=(
                    app.config['DEVICES'],
                    app.config['SINGLE_BOARD_DEVICES']
                )
            )

        # verify that the failure above did not mutate any state
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

    def test_007_register_plc(self):
        """ Test registering multiple PLC devices when a value is missing from
        the incoming config. Here, the first record is the malformed record.
        """
        # define the PLC config
        plc_devices = {
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'lockfile': '/tmp/test-lock',
                        'hardware_type': 'emulator',
                        'devices': [
                            {
                                'retry_limit': 3,
                                'timeout': 0.25,
                                'time_slice': 75,
                                'bps': 115200
                            },
                            {
                                'device_name': '/dev/ttyVapor002',
                                'retry_limit': 3,
                                'timeout': 0.25,
                                'time_slice': 75,
                                'bps': 115200
                            },
                            {
                                'device_name': '/dev/ttyVapor002',
                                'retry_limit': 3,
                                'timeout': 0.25,
                                'time_slice': 75,
                                'bps': 115200
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the plc device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        with self.assertRaises(KeyError):
            # register the plc device(s)
            PLCDevice.register(
                devicebus_config=plc_devices,
                app_config=app.config,
                app_cache=(
                    app.config['DEVICES'],
                    app.config['SINGLE_BOARD_DEVICES'],
                )
            )

        # verify that the failure above did not mutate any state
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

    def test_008_register_plc(self):
        """ Test registering multiple PLC devices when a value is missing from
        the incoming config. Here, the last record is the malformed record.
        """
        # define the PLC config
        plc_devices = {
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'lockfile': '/tmp/test-lock',
                        'hardware_type': 'emulator',
                        'devices': [
                            {
                                'device_name': '/dev/ttyVapor002',
                                'retry_limit': 3,
                                'timeout': 0.25,
                                'time_slice': 75,
                                'bps': 115200
                            },
                            {
                                'device_name': '/dev/ttyVapor002',
                                'retry_limit': 3,
                                'timeout': 0.25,
                                'time_slice': 75,
                                'bps': 115200
                            },
                            {
                                'retry_limit': 3,
                                'timeout': 0.25,
                                'time_slice': 75,
                                'bps': 115200
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the plc device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        with self.assertRaises(KeyError):
            # register the plc device(s)
            PLCDevice.register(
                devicebus_config=plc_devices,
                app_config=app.config,
                app_cache=(
                    app.config['DEVICES'],
                    app.config['SINGLE_BOARD_DEVICES']
                )
            )

        # we will still get only 4 devices populated here, even though we are
        # scanning more than 1 bus. this is because we are scanning the same
        # bus multiple times, and the board IDs will be the same for each scan
        single_board_devices = app.config['SINGLE_BOARD_DEVICES']
        self.assertIsInstance(single_board_devices, dict)
        self.assertEqual(len(single_board_devices), 4)
        for item in single_board_devices.values():
            self.assertIsInstance(item, PLCDevice)

    def test_009_register_ipmi(self):
        """ Test registering a single IPMI device.
        """
        # define the IPMI config
        ipmi_devices = {
            'scan_on_init': True,
            'device_initializer_threads': 1,
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'bmcs': [
                            {
                                'bmc_ip': 'ipmi-emulator-x64',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-1'],
                                'ip_addresses': ['192.168.1.100']
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the ipmi device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the ipmi device(s)
        IPMIDevice.register(
            devicebus_config=ipmi_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # now check that the starting state has been mutated to include
        # the newly registered device(s)
        board_ids = []
        devices = app.config['DEVICES']
        self.assertIsInstance(devices, dict)
        self.assertEqual(len(devices), len(ipmi_devices['config']['racks'][0]['bmcs']))
        for uid, device in devices.iteritems():
            self.assertIsInstance(uid, uuid.UUID)
            self.assertIsInstance(device, IPMIDevice)
            # get the board ids for each device - this is used in the
            # next block of tests
            board_ids.append(device.board_id)

        # test that we got the expected board id assignment
        for device in devices.values():
            self.assertIn(device.board_id, [0x40000000])

        single_board_devices = app.config['SINGLE_BOARD_DEVICES']
        self.assertIsInstance(single_board_devices, dict)
        # this equality value is dependent on the board id, the number of
        # hostnames and ip addresses per bmc record
        self.assertEqual(len(single_board_devices), 3)
        # now, ensure that all found board ids and all known hostnames + ip
        # addresses have entries here.
        for bid in board_ids:
            self.assertIn(bid, single_board_devices)
            self.assertIsInstance(single_board_devices[bid], IPMIDevice)

        for rack in ipmi_devices['config']['racks']:
            for bmc in rack['bmcs']:
                if 'hostnames' in bmc:
                    for hostname in bmc['hostnames']:
                        self.assertIn(hostname, single_board_devices)
                        self.assertIsInstance(single_board_devices[hostname], IPMIDevice)

                if 'ip_addresses' in bmc:
                    for ip_address in bmc['ip_addresses']:
                        self.assertIn(ip_address, single_board_devices)
                        self.assertIsInstance(single_board_devices[ip_address], IPMIDevice)

    def test_010_register_ipmi(self):
        """ Test registering a single IPMI device. In this case, the IPMI
        device config has multiple hostname and ip_address entries.
        """
        # define the IPMI config
        ipmi_devices = {
            'scan_on_init': True,
            'device_initializer_threads': 1,
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'bmcs': [
                            {
                                'bmc_ip': 'ipmi-emulator-x64',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-1', 'test-2', 'test-3'],
                                'ip_addresses': ['192.168.1.100', '192.168.2.100']
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the ipmi device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the ipmi device(s)
        IPMIDevice.register(
            devicebus_config=ipmi_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # now check that the starting state has been mutated to include
        # the newly registered device(s)
        board_ids = []
        devices = app.config['DEVICES']
        self.assertIsInstance(devices, dict)
        self.assertEqual(len(devices), len(ipmi_devices['config']['racks'][0]['bmcs']))
        for uid, device in devices.iteritems():
            self.assertIsInstance(uid, uuid.UUID)
            self.assertIsInstance(device, IPMIDevice)
            # get the board ids for each device - this is used in the
            # next block of tests
            board_ids.append(device.board_id)

        # test that we got the expected board id assignment
        for device in devices.values():
            self.assertIn(device.board_id, [0x40000000])

        single_board_devices = app.config['SINGLE_BOARD_DEVICES']
        self.assertIsInstance(single_board_devices, dict)
        # this equality value is dependent on the board id, the number of
        # hostnames and ip addresses per bmc record
        self.assertEqual(len(single_board_devices), 6)
        # now, ensure that all found board ids and all known hostnames + ip
        # addresses have entries here.
        for bid in board_ids:
            self.assertIn(bid, single_board_devices)
            self.assertIsInstance(single_board_devices[bid], IPMIDevice)

        for rack in ipmi_devices['config']['racks']:
            for bmc in rack['bmcs']:
                if 'hostnames' in bmc:
                    for hostname in bmc['hostnames']:
                        self.assertIn(hostname, single_board_devices)
                        self.assertIsInstance(single_board_devices[hostname], IPMIDevice)

                if 'ip_addresses' in bmc:
                    for ip_address in bmc['ip_addresses']:
                        self.assertIn(ip_address, single_board_devices)
                        self.assertIsInstance(single_board_devices[ip_address], IPMIDevice)

    def test_011_register_ipmi(self):
        """ Test registering a single IPMI device. In this case, the IPMI
        device config has no hostname and ip_address entries.
        """
        # define the IPMI config
        ipmi_devices = {
            'scan_on_init': True,
            'device_initializer_threads': 1,
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'bmcs': [
                            {
                                'bmc_ip': 'ipmi-emulator-x64',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN'
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the ipmi device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the ipmi device(s)
        IPMIDevice.register(
            devicebus_config=ipmi_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # now check that the starting state has been mutated to include
        # the newly registered device(s)
        board_ids = []
        devices = app.config['DEVICES']
        self.assertIsInstance(devices, dict)
        self.assertEqual(len(devices), len(ipmi_devices['config']['racks'][0]['bmcs']))
        for uid, device in devices.iteritems():
            self.assertIsInstance(uid, uuid.UUID)
            self.assertIsInstance(device, IPMIDevice)
            # get the board ids for each device - this is used in the
            # next block of tests
            board_ids.append(device.board_id)

        # test that we got the expected board id assignment
        for device in devices.values():
            self.assertIn(device.board_id, [0x40000000])

        single_board_devices = app.config['SINGLE_BOARD_DEVICES']
        self.assertIsInstance(single_board_devices, dict)
        # this equality value is dependent on the board id, the number of
        # hostnames and ip addresses per bmc record. in this case, even though
        # we have no ip_addresses or hostnames defined, we still get 2 entries
        # here because when ip addresses are not defined, the bmc_ip is placed
        # into the 'ip_addresses' list as well.
        self.assertEqual(len(single_board_devices), 2)
        # now, ensure that all found board ids and all known hostnames + ip
        # addresses have entries here.
        for bid in board_ids:
            self.assertIn(bid, single_board_devices)
            self.assertIsInstance(single_board_devices[bid], IPMIDevice)

        for rack in ipmi_devices['config']['racks']:
            for bmc in rack['bmcs']:
                if 'hostnames' in bmc:
                    for hostname in bmc['hostnames']:
                        self.assertIn(hostname, single_board_devices)
                        self.assertIsInstance(single_board_devices[hostname], IPMIDevice)

                if 'ip_addresses' in bmc:
                    for ip_address in bmc['ip_addresses']:
                        self.assertIn(ip_address, single_board_devices)
                        self.assertIsInstance(single_board_devices[ip_address], IPMIDevice)

    def test_012_register_ipmi(self):
        """ Test registering multiple IPMI devices.
        """
        # define the IPMI config
        ipmi_devices = {
            'scan_on_init': True,
            'device_initializer_threads': 1,
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'bmcs': [
                            {
                                'bmc_ip': 'ipmi-emulator-x64',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-1'],
                                'ip_addresses': ['192.168.1.100']
                            },
                            {
                                'bmc_ip': 'ipmi-emulator-x64',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-2'],
                                'ip_addresses': ['192.168.2.100']
                            },
                            {
                                'bmc_ip': 'ipmi-emulator-x64',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-3'],
                                'ip_addresses': ['192.168.3.100']
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the ipmi device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the ipmi device(s)
        IPMIDevice.register(
            devicebus_config=ipmi_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # now check that the starting state has been mutated to include
        # the newly registered device(s)
        board_ids = []
        devices = app.config['DEVICES']
        self.assertIsInstance(devices, dict)
        self.assertEqual(len(devices), len(ipmi_devices['config']['racks'][0]['bmcs']))
        for uid, device in devices.iteritems():
            self.assertIsInstance(uid, uuid.UUID)
            self.assertIsInstance(device, IPMIDevice)
            # get the board ids for each device - this is used in the
            # next block of tests
            board_ids.append(device.board_id)

        # test that we got the expected board id assignment
        for device in devices.values():
            self.assertIn(device.board_id, [0x40000000, 0x40000001, 0x40000002])

        single_board_devices = app.config['SINGLE_BOARD_DEVICES']
        self.assertIsInstance(single_board_devices, dict)
        # this equality value is dependent on the board id, the number of
        # hostnames and ip addresses per bmc record
        self.assertEqual(len(single_board_devices), 9)
        # now, ensure that all found board ids and all known hostnames + ip
        # addresses have entries here.
        for bid in board_ids:
            self.assertIn(bid, single_board_devices)
            self.assertIsInstance(single_board_devices[bid], IPMIDevice)

        for rack in ipmi_devices['config']['racks']:
            for bmc in rack['bmcs']:
                if 'hostnames' in bmc:
                    for hostname in bmc['hostnames']:
                        self.assertIn(hostname, single_board_devices)
                        self.assertIsInstance(single_board_devices[hostname], IPMIDevice)

                if 'ip_addresses' in bmc:
                    for ip_address in bmc['ip_addresses']:
                        self.assertIn(ip_address, single_board_devices)
                        self.assertIsInstance(single_board_devices[ip_address], IPMIDevice)

    def test_013_register_ipmi(self):
        """ Test registering no IPMI devices.
        """
        # define the IPMI config
        ipmi_devices = {}

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the ipmi device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the ipmi device(s)
        with self.assertRaises(ValueError):
            IPMIDevice.register(
                devicebus_config=ipmi_devices,
                app_config=app.config,
                app_cache=(
                    app.config['DEVICES'],
                    app.config['SINGLE_BOARD_DEVICES']
                )
            )

    def test_014_register_ipmi(self):
        """ Test registering no IPMI devices.
        """
        # define the IPMI config
        ipmi_devices = {
            'scan_on_init': True,
            'device_initializer_threads': 1,
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'bmcs': []
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the ipmi device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the ipmi device(s)
        IPMIDevice.register(
            devicebus_config=ipmi_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # now check that the starting state has not been mutated since there
        # are no records to register
        devices = app.config['DEVICES']
        self.assertIsInstance(devices, dict)
        self.assertEqual(len(devices), 0)

        single_board_devices = app.config['SINGLE_BOARD_DEVICES']
        self.assertIsInstance(single_board_devices, dict)
        self.assertEqual(len(single_board_devices), 0)

    def test_015_register_ipmi(self):
        """ Test registering a single IPMI device when other config already
        exists in the app config.
        """
        # define the IPMI config
        ipmi_devices = {
            'scan_on_init': True,
            'device_initializer_threads': 1,
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'bmcs': [
                            {
                                'bmc_ip': 'ipmi-emulator-x64',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-1'],
                                'ip_addresses': ['192.168.1.100']
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()

        _ipmi_device = IPMIDevice(
            app_cfg=app.config,
            counter=app.config['COUNTER'],
            **self.sample_ipmi_device
        )

        app.config['DEVICES'] = {uuid.uuid4(): _ipmi_device}
        app.config['SINGLE_BOARD_DEVICES'] = {
            _ipmi_device.board_id: _ipmi_device,
            self.sample_ipmi_device['hostnames'][0]: _ipmi_device,
            self.sample_ipmi_device['ip_addresses'][0]: _ipmi_device
        }

        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the ipmi device(s)
        self.assertEqual(len(app.config['DEVICES']), 1)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 3)

        # register the ipmi device(s)
        IPMIDevice.register(
            devicebus_config=ipmi_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # now check that the starting state has been mutated to include
        # the newly registered device(s)
        board_ids = []
        devices = app.config['DEVICES']
        self.assertIsInstance(devices, dict)
        self.assertEqual(len(devices), len(ipmi_devices['config']['racks'][0]['bmcs']) + 1)
        for uid, device in devices.iteritems():
            self.assertIsInstance(uid, uuid.UUID)
            self.assertIsInstance(device, IPMIDevice)
            # get the board ids for each device - this is used in the
            # next block of tests
            board_ids.append(device.board_id)

        # test that we got the expected board id assignment
        for device in devices.values():
            self.assertIn(
                device.board_id,
                [0x40000000, 0x40000014]  # 0x40000014 here because of hardcoded offset in self.sample_ipmi_device
            )

        single_board_devices = app.config['SINGLE_BOARD_DEVICES']
        self.assertIsInstance(single_board_devices, dict)
        # this equality value is dependent on the board id, the number of
        # hostnames and ip addresses per bmc record
        self.assertEqual(len(single_board_devices), 3 + 3)
        # now, ensure that all found board ids and all known hostnames + ip
        # addresses have entries here.
        for bid in board_ids:
            self.assertIn(bid, single_board_devices)
            self.assertIsInstance(single_board_devices[bid], IPMIDevice)

        for rack in ipmi_devices['config']['racks']:
            for bmc in rack['bmcs']:
                if 'hostnames' in bmc:
                    for hostname in bmc['hostnames']:
                        self.assertIn(hostname, single_board_devices)
                        self.assertIsInstance(single_board_devices[hostname], IPMIDevice)

                if 'ip_addresses' in bmc:
                    for ip_address in bmc['ip_addresses']:
                        self.assertIn(ip_address, single_board_devices)
                        self.assertIsInstance(single_board_devices[ip_address], IPMIDevice)

    def test_016_register_ipmi(self):
        """ Test registering a single IPMI device when other config already
        exists in the app config.
        """
        # define the IPMI config
        ipmi_devices = {
            'scan_on_init': True,
            'device_initializer_threads': 1,
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'bmcs': [
                            {
                                'bmc_ip': 'ipmi-emulator-x64',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-1'],
                                'ip_addresses': ['192.168.1.100']
                            },
                            {
                                'bmc_ip': 'ipmi-emulator-x64',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-2'],
                                'ip_addresses': ['192.168.2.100']
                            },
                            {
                                'bmc_ip': 'ipmi-emulator-x64',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-3'],
                                'ip_addresses': ['192.168.3.100']
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()

        _ipmi_device = IPMIDevice(
            app_cfg=app.config,
            counter=app.config['COUNTER'],
            **self.sample_ipmi_device
        )

        app.config['DEVICES'] = {uuid.uuid4(): _ipmi_device}
        app.config['SINGLE_BOARD_DEVICES'] = {
            _ipmi_device.board_id: _ipmi_device,
            self.sample_ipmi_device['hostnames'][0]: _ipmi_device,
            self.sample_ipmi_device['ip_addresses'][0]: _ipmi_device
        }

        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the ipmi device(s)
        self.assertEqual(len(app.config['DEVICES']), 1)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 3)

        # register the ipmi device(s)
        IPMIDevice.register(
            devicebus_config=ipmi_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # now check that the starting state has been mutated to include
        # the newly registered device(s)
        board_ids = []
        devices = app.config['DEVICES']
        self.assertIsInstance(devices, dict)
        self.assertEqual(len(devices), len(ipmi_devices['config']['racks'][0]['bmcs']) + 1)
        for uid, device in devices.iteritems():
            self.assertIsInstance(uid, uuid.UUID)
            self.assertIsInstance(device, IPMIDevice)
            # get the board ids for each device - this is used in the
            # next block of tests
            board_ids.append(device.board_id)

        # test that we got the expected board id assignment
        for device in devices.values():
            self.assertIn(
                device.board_id,
                [0x40000000, 0x40000001, 0x40000002, 0x40000014]  # 0x40000014 here because of hardcoded offset in
                                                                  # self.sample_ipmi_device
            )

        single_board_devices = app.config['SINGLE_BOARD_DEVICES']
        self.assertIsInstance(single_board_devices, dict)
        # this equality value is dependent on the board id, the number of
        # hostnames and ip addresses per bmc record
        self.assertEqual(len(single_board_devices), 9 + 3)
        # now, ensure that all found board ids and all known hostnames + ip
        # addresses have entries here.
        for bid in board_ids:
            self.assertIn(bid, single_board_devices)
            self.assertIsInstance(single_board_devices[bid], IPMIDevice)

        for rack in ipmi_devices['config']['racks']:
            for bmc in rack['bmcs']:
                if 'hostnames' in bmc:
                    for hostname in bmc['hostnames']:
                        self.assertIn(hostname, single_board_devices)
                        self.assertIsInstance(single_board_devices[hostname], IPMIDevice)

                if 'ip_addresses' in bmc:
                    for ip_address in bmc['ip_addresses']:
                        self.assertIn(ip_address, single_board_devices)
                        self.assertIsInstance(single_board_devices[ip_address], IPMIDevice)

    def test_017_register_ipmi(self):
        """ Test registering a single IPMI device when a device value is missing
        from the given config. This test should not raise because Synse still
        needs to start up.
        """
        # define the IPMI config
        ipmi_devices = {
            'scan_on_init': True,
            'device_initializer_threads': 1,
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'bmcs': [
                            {
                                'bmc_ip': 'ipmi-emulator-x64',
                                'bmc_port': 623,
                                'password': 'ADMIN',
                                'hostnames': ['test-1'],
                                'ip_addresses': ['192.168.1.100']
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the ipmi device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the ipmi device(s)
        IPMIDevice.register(
            devicebus_config=ipmi_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # verify that the failure did not mutate any state
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

    def test_018_register_ipmi(self):
        """ Test registering multiple IPMI devices when a device value is missing
        from the given config. In this case, the first record is malformed.
        This test should not raise because Synse still needs to start up.
        """
        # define the IPMI config
        ipmi_devices = {
            'scan_on_init': True,
            'device_initializer_threads': 1,
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'bmcs': [
                            {
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-1'],
                                'ip_addresses': ['192.168.1.100']
                            },
                            {
                                'bmc_ip': 'ipmi-emulator-x64',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-2'],
                                'ip_addresses': ['192.168.2.100']
                            },
                            {
                                'bmc_ip': 'ipmi-emulator-x64',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-3'],
                                'ip_addresses': ['192.168.3.100']
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the ipmi device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the ipmi device(s)
        IPMIDevice.register(
            devicebus_config=ipmi_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # because devices are being initialized in threads, we should expect to see
        # state mutated despite the bad config
        self.assertEqual(len(app.config['DEVICES']), 2)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 6)

    def test_019_register_ipmi(self):
        """ Test registering multiple IPMI devices when a device value is missing
        from the given config. In this case, the last record is malformed. This
        test should not raise because Synse still needs to start up.
        """
        # define the IPMI config
        ipmi_devices = {
            'scan_on_init': True,
            'device_initializer_threads': 1,
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'bmcs': [
                            {
                                'bmc_ip': 'ipmi-emulator-x64',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-1'],
                                'ip_addresses': ['192.168.1.100']
                            },
                            {
                                'bmc_ip': 'ipmi-emulator-x64',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-2'],
                                'ip_addresses': ['192.168.2.100']
                            },
                            {
                                'bmc_ip': 'ipmi-emulator-x64',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'hostnames': ['test-3'],
                                'ip_addresses': ['192.168.3.100']
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the ipmi device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the ipmi device(s)
        IPMIDevice.register(
            devicebus_config=ipmi_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # here, we will get mutated state since valid configs were found
        # before the invalid config. this is okay though because it raises
        # a ValueError which should cause Synse to terminate,
        # effectively disallowing invalid configuration.
        self.assertEqual(len(app.config['DEVICES']), 2)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 6)

    def test_020_register_ipmi(self):
        """ Test registering a single IPMI device. In this case, we will have
        duplicate hostnames - we want to be sure that the duplicate names do not
        cause duplicate records in the end state.
        """
        # define the IPMI config
        ipmi_devices = {
            'scan_on_init': True,
            'device_initializer_threads': 1,
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'bmcs': [
                            {
                                'bmc_ip': 'ipmi-emulator-x64',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-1', 'test-2', 'test-1'],
                                'ip_addresses': ['192.168.1.100']
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the ipmi device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the ipmi device(s)
        IPMIDevice.register(
            devicebus_config=ipmi_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # now check that the starting state has been mutated to include
        # the newly registered device(s)
        board_ids = []
        devices = app.config['DEVICES']
        self.assertIsInstance(devices, dict)
        self.assertEqual(len(devices), len(ipmi_devices['config']['racks'][0]['bmcs']))
        for uid, device in devices.iteritems():
            self.assertIsInstance(uid, uuid.UUID)
            self.assertIsInstance(device, IPMIDevice)
            # get the board ids for each device - this is used in the
            # next block of tests
            board_ids.append(device.board_id)

        # test that we got the expected board id assignment
        for device in devices.values():
            self.assertIn(device.board_id, [0x40000000])

        single_board_devices = app.config['SINGLE_BOARD_DEVICES']
        self.assertIsInstance(single_board_devices, dict)
        # this equality value is dependent on the board id, the number of
        # hostnames and ip addresses per bmc record
        self.assertEqual(len(single_board_devices), 4)
        # now, ensure that all found board ids and all known hostnames + ip
        # addresses have entries here.
        for bid in board_ids:
            self.assertIn(bid, single_board_devices)
            self.assertIsInstance(single_board_devices[bid], IPMIDevice)

        for rack in ipmi_devices['config']['racks']:
            for bmc in rack['bmcs']:
                if 'hostnames' in bmc:
                    for hostname in bmc['hostnames']:
                        self.assertIn(hostname, single_board_devices)
                        self.assertIsInstance(single_board_devices[hostname], IPMIDevice)

                if 'ip_addresses' in bmc:
                    for ip_address in bmc['ip_addresses']:
                        self.assertIn(ip_address, single_board_devices)
                        self.assertIsInstance(single_board_devices[ip_address], IPMIDevice)

    def test_021_register_ipmi(self):
        """ Test registering a single IPMI device. In this case, we will have
        duplicate ip_addresses - we want to be sure that the duplicate ips do not
        cause duplicate records in the end state.
        """
        # define the IPMI config
        ipmi_devices = {
            'scan_on_init': True,
            'device_initializer_threads': 1,
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'bmcs': [
                            {
                                'bmc_ip': 'ipmi-emulator-x64',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-1'],
                                'ip_addresses': ['192.168.1.100', '192.168.2.100', '192.168.1.100']
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the ipmi device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the ipmi device(s)
        IPMIDevice.register(
            devicebus_config=ipmi_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # now check that the starting state has been mutated to include
        # the newly registered device(s)
        board_ids = []
        devices = app.config['DEVICES']
        self.assertIsInstance(devices, dict)
        self.assertEqual(len(devices), len(ipmi_devices['config']['racks'][0]['bmcs']))
        for uid, device in devices.iteritems():
            self.assertIsInstance(uid, uuid.UUID)
            self.assertIsInstance(device, IPMIDevice)
            # get the board ids for each device - this is used in the
            # next block of tests
            board_ids.append(device.board_id)

        # test that we got the expected board id assignment
        for device in devices.values():
            self.assertIn(device.board_id, [0x40000000])

        single_board_devices = app.config['SINGLE_BOARD_DEVICES']
        self.assertIsInstance(single_board_devices, dict)
        # this equality value is dependent on the board id, the number of
        # hostnames and ip addresses per bmc record
        self.assertEqual(len(single_board_devices), 4)
        # now, ensure that all found board ids and all known hostnames + ip
        # addresses have entries here.
        for bid in board_ids:
            self.assertIn(bid, single_board_devices)
            self.assertIsInstance(single_board_devices[bid], IPMIDevice)

        for rack in ipmi_devices['config']['racks']:
            for bmc in rack['bmcs']:
                if 'hostnames' in bmc:
                    for hostname in bmc['hostnames']:
                        self.assertIn(hostname, single_board_devices)
                        self.assertIsInstance(single_board_devices[hostname], IPMIDevice)

                if 'ip_addresses' in bmc:
                    for ip_address in bmc['ip_addresses']:
                        self.assertIn(ip_address, single_board_devices)
                        self.assertIsInstance(single_board_devices[ip_address], IPMIDevice)

    def test_022_register_ipmi(self):
        """ Test registering a single IPMI device, where the provided IP will not resolve.

        This should not cause registration failure, but should generate a notification.
        """
        # define the IPMI config
        ipmi_devices = {
            'scan_on_init': True,
            'device_initializer_threads': 1,
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'bmcs': [
                            {
                                'bmc_ip': '192.168.10.10',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-1'],
                                'ip_addresses': ['192.168.1.100']
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the ipmi device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the ipmi device(s)
        IPMIDevice.register(
            devicebus_config=ipmi_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # now check that the starting state has been mutated to include
        # the newly registered device(s)
        board_ids = []
        devices = app.config['DEVICES']
        self.assertIsInstance(devices, dict)
        self.assertEqual(len(devices), len(ipmi_devices['config']['racks'][0]['bmcs']))
        for uid, device in devices.iteritems():
            self.assertIsInstance(uid, uuid.UUID)
            self.assertIsInstance(device, IPMIDevice)
            # get the board ids for each device - this is used in the
            # next block of tests
            board_ids.append(device.board_id)

        # test that we got the expected board id assignment
        for device in devices.values():
            self.assertIn(device.board_id, [0x40000000])

        single_board_devices = app.config['SINGLE_BOARD_DEVICES']
        self.assertIsInstance(single_board_devices, dict)
        # this equality value is dependent on the board id, the number of
        # hostnames and ip addresses per bmc record
        self.assertEqual(len(single_board_devices), 3)
        # now, ensure that all found board ids and all known hostnames + ip
        # addresses have entries here.
        for bid in board_ids:
            self.assertIn(bid, single_board_devices)
            self.assertIsInstance(single_board_devices[bid], IPMIDevice)

        for rack in ipmi_devices['config']['racks']:
            for bmc in rack['bmcs']:
                if 'hostnames' in bmc:
                    for hostname in bmc['hostnames']:
                        self.assertIn(hostname, single_board_devices)
                        self.assertIsInstance(single_board_devices[hostname], IPMIDevice)

                if 'ip_addresses' in bmc:
                    for ip_address in bmc['ip_addresses']:
                        self.assertIn(ip_address, single_board_devices)
                        self.assertIsInstance(single_board_devices[ip_address], IPMIDevice)

    def test_023_register_ipmi(self):
        """ Test registering multiple IPMI devices, where one of the provided IP will
        not resolve.

        This should not cause registration failure, but should generate a notification.
        """
        # define the IPMI config
        ipmi_devices = {
            'scan_on_init': True,
            'device_initializer_threads': 1,
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'bmcs': [
                            {
                                'bmc_ip': 'ipmi-emulator-x64',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-1'],
                                'ip_addresses': ['192.168.1.100']
                            },
                            {
                                'bmc_ip': '192.168.10.10',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-2'],
                                'ip_addresses': ['192.168.2.100']
                            },
                            {
                                'bmc_ip': 'ipmi-emulator-x64',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-3'],
                                'ip_addresses': ['192.168.3.100']
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the ipmi device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the ipmi device(s)
        IPMIDevice.register(
            devicebus_config=ipmi_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # now check that the starting state has been mutated to include
        # the newly registered device(s)
        board_ids = []
        devices = app.config['DEVICES']
        self.assertIsInstance(devices, dict)
        self.assertEqual(len(devices), len(ipmi_devices['config']['racks'][0]['bmcs']))
        for uid, device in devices.iteritems():
            self.assertIsInstance(uid, uuid.UUID)
            self.assertIsInstance(device, IPMIDevice)
            # get the board ids for each device - this is used in the
            # next block of tests
            board_ids.append(device.board_id)

        # test that we got the expected board id assignment
        for device in devices.values():
            self.assertIn(device.board_id, [0x40000000, 0x40000001, 0x40000002])

        single_board_devices = app.config['SINGLE_BOARD_DEVICES']
        self.assertIsInstance(single_board_devices, dict)
        # this equality value is dependent on the board id, the number of
        # hostnames and ip addresses per bmc record
        self.assertEqual(len(single_board_devices), 9)
        # now, ensure that all found board ids and all known hostnames + ip
        # addresses have entries here.
        for bid in board_ids:
            self.assertIn(bid, single_board_devices)
            self.assertIsInstance(single_board_devices[bid], IPMIDevice)

        for rack in ipmi_devices['config']['racks']:
            for bmc in rack['bmcs']:
                if 'hostnames' in bmc:
                    for hostname in bmc['hostnames']:
                        self.assertIn(hostname, single_board_devices)
                        self.assertIsInstance(single_board_devices[hostname], IPMIDevice)

                if 'ip_addresses' in bmc:
                    for ip_address in bmc['ip_addresses']:
                        self.assertIn(ip_address, single_board_devices)
                        self.assertIsInstance(single_board_devices[ip_address], IPMIDevice)

    def test_024_register_ipmi(self):
        """ Test registering multiple IPMI devices, where multiple of the provided IPs will
        not resolve.

        This should not cause registration failure, but should generate notifications.
        """
        # define the IPMI config
        ipmi_devices = {
            'scan_on_init': True,
            'device_initializer_threads': 1,
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'bmcs': [
                            {
                                'bmc_ip': 'ipmi-emulator-x64',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-1'],
                                'ip_addresses': ['192.168.1.100']
                            },
                            {
                                'bmc_ip': '192.168.10.10',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-2'],
                                'ip_addresses': ['192.168.2.100']
                            },
                            {
                                'bmc_ip': '192.168.10.11',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-3'],
                                'ip_addresses': ['192.168.3.100']
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the ipmi device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the ipmi device(s)
        IPMIDevice.register(
            devicebus_config=ipmi_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # now check that the starting state has been mutated to include
        # the newly registered device(s)
        board_ids = []
        devices = app.config['DEVICES']
        self.assertIsInstance(devices, dict)
        self.assertEqual(len(devices), len(ipmi_devices['config']['racks'][0]['bmcs']))
        for uid, device in devices.iteritems():
            self.assertIsInstance(uid, uuid.UUID)
            self.assertIsInstance(device, IPMIDevice)
            # get the board ids for each device - this is used in the
            # next block of tests
            board_ids.append(device.board_id)

        # test that we got the expected board id assignment
        for device in devices.values():
            self.assertIn(device.board_id, [0x40000000, 0x40000001, 0x40000002])

        single_board_devices = app.config['SINGLE_BOARD_DEVICES']
        self.assertIsInstance(single_board_devices, dict)
        # this equality value is dependent on the board id, the number of
        # hostnames and ip addresses per bmc record
        self.assertEqual(len(single_board_devices), 9)
        # now, ensure that all found board ids and all known hostnames + ip
        # addresses have entries here.
        for bid in board_ids:
            self.assertIn(bid, single_board_devices)
            self.assertIsInstance(single_board_devices[bid], IPMIDevice)

        for rack in ipmi_devices['config']['racks']:
            for bmc in rack['bmcs']:
                if 'hostnames' in bmc:
                    for hostname in bmc['hostnames']:
                        self.assertIn(hostname, single_board_devices)
                        self.assertIsInstance(single_board_devices[hostname], IPMIDevice)

                if 'ip_addresses' in bmc:
                    for ip_address in bmc['ip_addresses']:
                        self.assertIn(ip_address, single_board_devices)
                        self.assertIsInstance(single_board_devices[ip_address], IPMIDevice)

    def test_025_register_ipmi(self):
        """ Test registering an IPMI device where an invalid hostname is given as the BMC
        IP. Unlike the case where an IP can be specified and it need not connect (e.g. can
        timeout without failing registration), this will fail registration under the guise
        of 'misconfiguration', since the provided hostname is not defined. This
        test should not raise because Synse still needs to start up.
        """
        # define the IPMI config
        ipmi_devices = {
            'scan_on_init': True,
            'device_initializer_threads': 1,
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'bmcs': [
                            {
                                'bmc_ip': 'invalid-emulator-host',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-1'],
                                'ip_addresses': ['192.168.1.100']
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the ipmi device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the ipmi device(s)
        IPMIDevice.register(
            devicebus_config=ipmi_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # since the device failed to register, we should not see any mutations to
        # the state.
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

    def test_026_register_ipmi(self):
        """ Test registering multiple IPMI devices when a device value is missing
        from the given config. In this case, the last record is malformed. This
        test should not raise because Synse still needs to start up.
        """
        # define the IPMI config
        ipmi_devices = {
            'scan_on_init': True,
            'device_initializer_threads': 1,
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'bmcs': [
                            {
                                'bmc_ip': 'ipmi-emulator-x64',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-1'],
                                'ip_addresses': ['192.168.1.100']
                            },
                            {
                                'bmc_ip': 'ipmi-emulator-x64',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'password': 'ADMIN',
                                'hostnames': ['test-2'],
                                'ip_addresses': ['192.168.2.100']
                            },
                            {
                                'bmc_ip': 'invalid-emulator-host',
                                'bmc_port': 623,
                                'username': 'ADMIN',
                                'hostnames': ['test-3'],
                                'ip_addresses': ['192.168.3.100']
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the ipmi device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the ipmi device(s)
        IPMIDevice.register(
            devicebus_config=ipmi_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # here, we will get mutated state since valid configs were found
        # before the invalid config. this is okay though because it raises
        # a ValueError which should cause Synse to terminate,
        # effectively disallowing invalid configuration.
        self.assertEqual(len(app.config['DEVICES']), 2)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 6)

    def test_031_register_redfish(self):
        """ Test registering a single Redfish device.
        """
        # define the Redfish config
        redfish_devices = {
            'scan_on_init': True,
            'device_initializer_threads': 1,
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'servers': [
                            {
                                'redfish_ip': 'redfish-emulator-x64',
                                'redfish_port': 5040,
                                'timeout': 5,
                                'username': 'root',
                                'password': 'redfish',
                                'hostnames': ['127.0.0.1'],
                                'ip_addresses': ['127.0.0.1']
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the redfish device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the redfish device(s)
        RedfishDevice.register(
            devicebus_config=redfish_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # now check that the starting state has been mutated to include
        # the newly registered device(s)
        board_ids = []
        devices = app.config['DEVICES']
        self.assertIsInstance(devices, dict)
        self.assertEqual(len(devices), len(redfish_devices['config']['racks'][0]['servers']))
        for uid, device in devices.iteritems():
            self.assertIsInstance(uid, uuid.UUID)
            self.assertIsInstance(device, RedfishDevice)
            # get the board ids for each device - this is used in the
            # next block of tests
            board_ids.append(device.board_id)

        # test that we got the expected board id assignment
        for device in devices.values():
            self.assertIn(device.board_id, [0x70000000])

        single_board_devices = app.config['SINGLE_BOARD_DEVICES']
        self.assertIsInstance(single_board_devices, dict)
        # this equality value is dependent on the board id, the number of
        # hostnames and ip addresses per server record
        self.assertEqual(len(single_board_devices), 2)
        # now, ensure that all found board ids and all known hostnames + ip
        # addresses have entries here.
        for bid in board_ids:
            self.assertIn(bid, single_board_devices)
            self.assertIsInstance(single_board_devices[bid], RedfishDevice)

        for rack in redfish_devices['config']['racks']:
            for server in rack['servers']:
                if 'hostnames' in server:
                    for hostname in server['hostnames']:
                        self.assertIn(hostname, single_board_devices)
                        self.assertIsInstance(single_board_devices[hostname], RedfishDevice)

                if 'ip_addresses' in server:
                    for ip_address in server['ip_addresses']:
                        self.assertIn(ip_address, single_board_devices)
                        self.assertIsInstance(single_board_devices[ip_address], RedfishDevice)

    def test_032_register_redfish(self):
        """ Test registering a single Redfish device. In this case, the Redfish
        device config has no hostname, ip_address, or timeout entries.
        """
        # define the Redfish config
        redfish_devices = {
            'scan_on_init': True,
            'device_initializer_threads': 1,
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'servers': [
                            {
                                'redfish_ip': 'redfish-emulator-x64',
                                'redfish_port': 5040,
                                'username': 'root',
                                'password': 'redfish'
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the redfish device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the redfish device(s)
        RedfishDevice.register(
            devicebus_config=redfish_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # now check that the starting state has been mutated to include
        # the newly registered device(s)
        board_ids = []
        devices = app.config['DEVICES']
        self.assertIsInstance(devices, dict)
        self.assertEqual(len(devices), len(redfish_devices['config']['racks'][0]['servers']))
        for uid, device in devices.iteritems():
            self.assertIsInstance(uid, uuid.UUID)
            self.assertIsInstance(device, RedfishDevice)
            # get the board ids for each device - this is used in the
            # next block of tests
            board_ids.append(device.board_id)

        # test that we got the expected board id assignment
        for device in devices.values():
            self.assertIn(device.board_id, [0x70000000])

        single_board_devices = app.config['SINGLE_BOARD_DEVICES']
        self.assertIsInstance(single_board_devices, dict)
        # this equality value is dependent on the board id, the number of
        # hostnames and ip addresses per server record. in this case, even though
        # we have no ip_addresses or hostnames defined, we still get 2 entries
        # here because when ip addresses are not defined, the redfish_ip is placed
        # into the 'ip_addresses' list as well.
        self.assertEqual(len(single_board_devices), 2)
        # now, ensure that all found board ids and all known hostnames + ip
        # addresses have entries here.
        for bid in board_ids:
            self.assertIn(bid, single_board_devices)
            self.assertIsInstance(single_board_devices[bid], RedfishDevice)

        for rack in redfish_devices['config']['racks']:
            for server in rack['servers']:
                if 'hostnames' in server:
                    for hostname in server['hostnames']:
                        self.assertIn(hostname, single_board_devices)
                        self.assertIsInstance(single_board_devices[hostname], RedfishDevice)

                if 'ip_addresses' in server:
                    for ip_address in server['ip_addresses']:
                        self.assertIn(ip_address, single_board_devices)
                        self.assertIsInstance(single_board_devices[ip_address], RedfishDevice)

    def test_033_register_redfish(self):
        """ Test registering no Redfish devices.
        """
        # define the Redfish config
        redfish_devices = {}

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the redfish device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the redfish device(s)
        with self.assertRaises(ValueError):
            RedfishDevice.register(
                devicebus_config=redfish_devices,
                app_config=app.config,
                app_cache=(
                    app.config['DEVICES'],
                    app.config['SINGLE_BOARD_DEVICES']
                )
            )

    def test_034_register_redfish(self):
        """ Test registering no Redfish devices.
        """
        # define the Redfish config
        redfish_devices = {
            'scan_on_init': True,
            'device_initializer_threads': 1,
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'servers': []
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the redfish device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the redfish device(s)
        RedfishDevice.register(
            devicebus_config=redfish_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # now check that the starting state has not been mutated since there
        # are no records to register
        devices = app.config['DEVICES']
        self.assertIsInstance(devices, dict)
        self.assertEqual(len(devices), 0)

        single_board_devices = app.config['SINGLE_BOARD_DEVICES']
        self.assertIsInstance(single_board_devices, dict)
        self.assertEqual(len(single_board_devices), 0)

    def test_035_register_redfish(self):
        """ Test registering a single Redfish device when a device value is missing
        from the given config.
        """
        # define the Redfish config
        redfish_devices = {
            'scan_on_init': True,
            'device_initializer_threads': 1,
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'servers': [
                            {
                                'redfish_ip': 'redfish-emulator-x64',
                                'redfish_port': 5040,
                                'timeout': 5,
                                'password': 'redfish',
                                'hostnames': ['127.0.0.1'],
                                'ip_addresses': ['127.0.0.1']
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the redfish device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        with self.assertRaises(KeyError):
            # register the redfish device(s)
            RedfishDevice.register(
                devicebus_config=redfish_devices,
                app_config=app.config,
                app_cache=(
                    app.config['DEVICES'],
                    app.config['SINGLE_BOARD_DEVICES']
                )
            )

        # verify that the failure did not mutate any state
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

    def test_036_register_redfish(self):
        """ Test registering a single Redfish device. In this case, we will have
        duplicate hostnames - we want to be sure that the duplicate names do not
        cause duplicate records in the end state.
        """
        # define the Redfish config
        redfish_devices = {
            'scan_on_init': True,
            'device_initializer_threads': 1,
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'servers': [
                            {
                                'redfish_ip': 'redfish-emulator-x64',
                                'redfish_port': 5040,
                                'timeout': 5,
                                'username': 'root',
                                'password': 'redfish',
                                'hostnames': ['127.0.0.1', '127.0.0.1'],
                                'ip_addresses': ['127.0.0.1']
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the redfish device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the redfish device(s)
        RedfishDevice.register(
            devicebus_config=redfish_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # now check that the starting state has been mutated to include
        # the newly registered device(s)
        board_ids = []
        devices = app.config['DEVICES']
        self.assertIsInstance(devices, dict)
        self.assertEqual(len(devices), len(redfish_devices['config']['racks'][0]['servers']))
        for uid, device in devices.iteritems():
            self.assertIsInstance(uid, uuid.UUID)
            self.assertIsInstance(device, RedfishDevice)
            # get the board ids for each device - this is used in the
            # next block of tests
            board_ids.append(device.board_id)

        # test that we got the expected board id assignment
        for device in devices.values():
            self.assertIn(device.board_id, [0x70000000])

        single_board_devices = app.config['SINGLE_BOARD_DEVICES']
        self.assertIsInstance(single_board_devices, dict)
        # this equality value is dependent on the board id, the number of
        # hostnames and ip addresses per redfish record
        self.assertEqual(len(single_board_devices), 2)
        self.assertIn('127.0.0.1', single_board_devices)
        # now, ensure that all found board ids and all known hostnames + ip
        # addresses have entries here.
        for bid in board_ids:
            self.assertIn(bid, single_board_devices)
            self.assertIsInstance(single_board_devices[bid], RedfishDevice)

        for rack in redfish_devices['config']['racks']:
            for server in rack['servers']:
                if 'hostnames' in server:
                    for hostname in server['hostnames']:
                        self.assertIn(hostname, single_board_devices)
                        self.assertIsInstance(single_board_devices[hostname], RedfishDevice)

                if 'ip_addresses' in server:
                    for ip_address in server['ip_addresses']:
                        self.assertIn(ip_address, single_board_devices)
                        self.assertIsInstance(single_board_devices[ip_address], RedfishDevice)

    def test_037_register_redfish(self):
        """ Test registering a single Redfish device. In this case, we will have
        duplicate ip_addresses - we want to be sure that the duplicate ips do not
        cause duplicate records in the end state.
        """
        # define the Redfish config
        redfish_devices = {
            'scan_on_init': True,
            'device_initializer_threads': 1,
            'config': {
                'racks': [
                    {
                        'rack_id': 'rack_1',
                        'servers': [
                            {
                                'redfish_ip': 'redfish-emulator-x64',
                                'redfish_port': 5040,
                                'timeout': 5,
                                'username': 'root',
                                'password': 'redfish',
                                'hostnames': ['127.0.0.1'],
                                'ip_addresses': ['127.0.0.1', '127.0.0.1']
                            }
                        ]
                    }
                ]
            }
        }

        # define the mock app config and override the synse app
        # definition with the mock app
        app = MockApp()
        sb.app = app

        # verify that the starting state of the app config does not
        # contain information on the redfish device(s)
        self.assertEqual(len(app.config['DEVICES']), 0)
        self.assertEqual(len(app.config['SINGLE_BOARD_DEVICES']), 0)

        # register the redfish device(s)
        RedfishDevice.register(
            devicebus_config=redfish_devices,
            app_config=app.config,
            app_cache=(
                app.config['DEVICES'],
                app.config['SINGLE_BOARD_DEVICES']
            )
        )

        # now check that the starting state has been mutated to include
        # the newly registered device(s)
        board_ids = []
        devices = app.config['DEVICES']
        self.assertIsInstance(devices, dict)
        self.assertEqual(len(devices), len(redfish_devices['config']['racks'][0]['servers']))
        for uid, device in devices.iteritems():
            self.assertIsInstance(uid, uuid.UUID)
            self.assertIsInstance(device, RedfishDevice)
            # get the board ids for each device - this is used in the
            # next block of tests
            board_ids.append(device.board_id)

        # test that we got the expected board id assignment
        for device in devices.values():
            self.assertIn(device.board_id, [0x70000000])

        single_board_devices = app.config['SINGLE_BOARD_DEVICES']
        self.assertIsInstance(single_board_devices, dict)
        # this equality value is dependent on the board id, the number of
        # hostnames and ip addresses per redfish record
        self.assertEqual(len(single_board_devices), 2)
        # now, ensure that all found board ids and all known hostnames + ip
        # addresses have entries here.
        for bid in board_ids:
            self.assertIn(bid, single_board_devices)
            self.assertIsInstance(single_board_devices[bid], RedfishDevice)

        for rack in redfish_devices['config']['racks']:
            for server in rack['servers']:
                if 'hostnames' in server:
                    for hostname in server['hostnames']:
                        self.assertIn(hostname, single_board_devices)
                        self.assertIsInstance(single_board_devices[hostname], RedfishDevice)

                if 'ip_addresses' in server:
                    for ip_address in server['ip_addresses']:
                        self.assertIn(ip_address, single_board_devices)
                        self.assertIsInstance(single_board_devices[ip_address], RedfishDevice)
