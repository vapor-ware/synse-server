#!/usr/bin/env python
""" OpenDCRE Southbound Supported Device Command Tests

    Author: Erick Daniszewski
    Date:   10/27/2016

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
from itertools import count
import unittest

from opendcre_southbound.devicebus.devices.ipmi.ipmi_device import IPMIDevice

from opendcre_southbound.devicebus.command_factory import CommandFactory
from opendcre_southbound.errors import CommandNotSupported


class SupportedDeviceCommandsTestCase(unittest.TestCase):
    """ Check that devices handle the expected commands and fail
    appropriately when handing unsupported devices.

    In these cases, commands which are supported will typically fail here
    with KeyError, as we are not specifying the data in the command object
    being passed to the handle() method.

    Commands that are not supported should fail with CommandNotSupported
    errors.
    """
    @classmethod
    def setUpClass(cls):

        counter = count()
        ipmi_kwargs = {
            'bmc_ip': 'localhost',
            'bmc_rack': 'rack_1',
            'username': 'ADMIN',
            'password': 'ADMIN',
            'board_offset': 0,
            'board_id_range': (0, 0),
            'device_id': 'test_device'
        }
        cls.ipmi = IPMIDevice({'SCAN_CACHE': '/tmp/not-a-file.json'}, counter, **ipmi_kwargs)

        command_fac = CommandFactory(counter)

        cls._version = command_fac.get_version_command({})
        cls._read = command_fac.get_read_command({})
        cls._scan = command_fac.get_scan_command({})
        cls._scan_all = command_fac.get_scan_all_command({})
        cls._write = command_fac.get_write_command({})
        cls._power = command_fac.get_power_command({})
        cls._asset = command_fac.get_asset_command({})
        cls._boot_tgt = command_fac.get_boot_target_command({})
        cls._location = command_fac.get_location_command({})
        cls._chamber_led = command_fac.get_chamber_led_command({})
        cls._led = command_fac.get_led_command({})
        cls._fan = command_fac.get_fan_command({})
        cls._host_info = command_fac.get_host_info_command({})
        cls._retry = command_fac.get_retry_command({})

    def test_000_ipmi(self):
        """ Test the IPMI device for VERSION command support.
        """
        self.ipmi.handle(self._version)

    def test_001_ipmi(self):
        """ Test the IPMI device for SCAN command support.
        """
        self.ipmi.handle(self._scan)

    def test_002_ipmi(self):
        """ Test the IPMI device for SCAN_ALL command support.
        """
        self.ipmi.handle(self._scan_all)

    def test_003_ipmi(self):
        """ Test the IPMI device for READ command support.
        """
        with self.assertRaises(KeyError):
            self.ipmi.handle(self._read)

    def test_004_ipmi(self):
        """ Test the IPMI device for WRITE command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.ipmi.handle(self._write)

    def test_005_ipmi(self):
        """ Test the IPMI device for POWER command support.
        """
        with self.assertRaises(KeyError):
            self.ipmi.handle(self._power)

    def test_006_ipmi(self):
        """ Test the IPMI device for ASSET command support.
        """
        with self.assertRaises(KeyError):
            self.ipmi.handle(self._asset)

    def test_007_ipmi(self):
        """ Test the IPMI device for BOOT_TARGET command support.
        """
        with self.assertRaises(KeyError):
            self.ipmi.handle(self._boot_tgt)

    def test_008_ipmi(self):
        """ Test the IPMI device for LOCATION command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.ipmi.handle(self._location)

    def test_009_ipmi(self):
        """ Test the IPMI device for CHAMBER_LED command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.ipmi.handle(self._chamber_led)

    def test_010_ipmi(self):
        """ Test the IPMI device for LED command support.
        """
        with self.assertRaises(KeyError):
            self.ipmi.handle(self._led)

    def test_011_ipmi(self):
        """ Test the IPMI device for FAN command support.
        """
        with self.assertRaises(KeyError):
            self.ipmi.handle(self._fan)

    def test_012_ipmi(self):
        """ Test the IPMI device for HOST_INFO command support.
        """
        self.ipmi.handle(self._host_info)

    def test_013_ipmi(self):
        """ Test the IPMI device for RETRY command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.ipmi.handle(self._retry)
