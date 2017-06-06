#!/usr/bin/env python
""" Synse Supported Device Command Tests

    Author: Erick Daniszewski
    Date:   10/27/2016

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
from itertools import count
import unittest

from synse.devicebus.devices.ipmi.ipmi_device import IPMIDevice

from synse.devicebus.devices.i2c.max11608_adc_thermistor import Max11608Thermistor
from synse.devicebus.devices.i2c.pca9632_led import PCA9632Led
from synse.devicebus.devices.i2c.sdp610_pressure import SDP610Pressure

from synse.devicebus.devices.rs485.sht31_humidity import SHT31Humidity
from synse.devicebus.devices.rs485.d6f_w10a1_airflow import D6FW10A1Airflow
from synse.devicebus.devices.rs485.gs3_2010_fan_controller import GS32010Fan

from synse.devicebus.command_factory import CommandFactory
from synse.errors import CommandNotSupported


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

        i2c_kwargs = {
            'lockfile': '/tmp/test',
            'device_name': 'test',
            'rack_id': 'rack_2',
            'board_offset': 0,
            'board_id_range': (0, 0),
            'device_id': 'test_device',
            'channel': '0',
            'altitude': 0
        }
        cls.max11608thermistor = Max11608Thermistor(**i2c_kwargs)
        cls.pca9632led = PCA9632Led(**i2c_kwargs)
        cls.sdp610pressure = SDP610Pressure(**i2c_kwargs)

        rs485_kwargs = {
            'lockfile': '/tmp/test',
            'device_name': 'test-device',
            'rack_id': 'rack_3',
            'device_unit': 0,
            'board_offset': 0,
            'board_id_range': (0, 0),
            'device_id': 'test_device',
            'base_address': '0',
            'device_model': 'test_device',
        }
        cls.sht31humidity = SHT31Humidity(**rs485_kwargs)
        cls.d6fw10a1airflow = D6FW10A1Airflow(**rs485_kwargs)
        cls.gs32010fan = GS32010Fan(**rs485_kwargs)

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

    def test_014_max11608thermistor(self):
        """ Test the I2C device for VERSION command support. This command is now supported.
        """
        self.max11608thermistor.handle(self._version)

    def test_015_max11608thermistor(self):
        """ Test the I2C device for SCAN command support.
        """
        self.max11608thermistor.handle(self._scan)

    def test_016_max11608thermistor(self):
        """ Test the I2C device for SCAN_ALL command support.
        """
        self.max11608thermistor.handle(self._scan_all)

    def test_017_max11608thermistor(self):
        """ Test the I2C device for READ command support.
        """
        with self.assertRaises(KeyError):
            self.max11608thermistor.handle(self._read)

    def test_018_max11608thermistor(self):
        """ Test the I2C device for WRITE command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.max11608thermistor.handle(self._write)

    def test_019_max11608thermistor(self):
        """ Test the I2C device for POWER command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.max11608thermistor.handle(self._power)

    def test_020_max11608thermistor(self):
        """ Test the I2C device for ASSET command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.max11608thermistor.handle(self._asset)

    def test_021_max11608thermistor(self):
        """ Test the I2C device for BOOT_TARGET command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.max11608thermistor.handle(self._boot_tgt)

    def test_022_max11608thermistor(self):
        """ Test the I2C device for LOCATION command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.max11608thermistor.handle(self._location)

    def test_023_max11608thermistor(self):
        """ Test the I2C device for CHAMBER_LED command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.max11608thermistor.handle(self._chamber_led)

    def test_024_max11608thermistor(self):
        """ Test the I2C device for LED command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.max11608thermistor.handle(self._led)

    def test_025_max11608thermistor(self):
        """ Test the I2C device for FAN command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.max11608thermistor.handle(self._fan)

    def test_026_max11608thermistor(self):
        """ Test the I2C device for HOST_INFO command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.max11608thermistor.handle(self._host_info)

    def test_027_max11608thermistor(self):
        """ Test the I2C device for RETRY command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.max11608thermistor.handle(self._retry)

    def test_028_pca9632led(self):
        """ Test the I2C device for VERSION command support. This command is now supported.
        """
        self.pca9632led.handle(self._version)

    def test_029_pca9632led(self):
        """ Test the I2C device for SCAN command support.
        """
        self.pca9632led.handle(self._scan)

    def test_030_pca9632led(self):
        """ Test the I2C device for SCAN_ALL command support.
        """
        self.pca9632led.handle(self._scan_all)

    def test_031_pca9632led(self):
        """ Test the I2C device for READ command support.
        """
        with self.assertRaises(KeyError):
            self.pca9632led.handle(self._read)

    def test_032_pca9632led(self):
        """ Test the I2C device for WRITE command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.pca9632led.handle(self._write)

    def test_033_pca9632led(self):
        """ Test the I2C device for POWER command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.pca9632led.handle(self._power)

    def test_034_pca9632led(self):
        """ Test the I2C device for ASSET command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.pca9632led.handle(self._asset)

    def test_035_pca9632led(self):
        """ Test the I2C device for BOOT_TARGET command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.pca9632led.handle(self._boot_tgt)

    def test_036_pca9632led(self):
        """ Test the I2C device for LOCATION command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.pca9632led.handle(self._location)

    def test_037_pca9632led(self):
        """ Test the I2C device for CHAMBER_LED command support.
        """
        with self.assertRaises(KeyError):
            self.pca9632led.handle(self._chamber_led)

    def test_038_pca9632led(self):
        """ Test the I2C device for LED command support.
        """
        with self.assertRaises(KeyError):
            self.pca9632led.handle(self._led)

    def test_039_pca9632led(self):
        """ Test the I2C device for FAN command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.pca9632led.handle(self._fan)

    def test_040_pca9632led(self):
        """ Test the I2C device for HOST_INFO command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.pca9632led.handle(self._host_info)

    def test_041_pca9632led(self):
        """ Test the I2C device for RETRY command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.pca9632led.handle(self._retry)

    def test_042_sdp610pressure(self):
        """ Test the I2C device for VERSION command support. This command is now supported.
        """
        self.sdp610pressure.handle(self._version)

    def test_043_sdp610pressure(self):
        """ Test the I2C device for SCAN command support.
        """
        self.sdp610pressure.handle(self._scan)

    def test_044_sdp610pressure(self):
        """ Test the I2C device for SCAN_ALL command support.
        """
        self.sdp610pressure.handle(self._scan_all)

    def test_045_sdp610pressure(self):
        """ Test the I2C device for READ command support.
        """
        with self.assertRaises(KeyError):
            self.sdp610pressure.handle(self._read)

    def test_046_sdp610pressure(self):
        """ Test the I2C device for WRITE command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.sdp610pressure.handle(self._write)

    def test_047_sdp610pressure(self):
        """ Test the I2C device for POWER command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.sdp610pressure.handle(self._power)

    def test_048_sdp610pressure(self):
        """ Test the I2C device for ASSET command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.sdp610pressure.handle(self._asset)

    def test_049_sdp610pressure(self):
        """ Test the I2C device for BOOT_TARGET command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.sdp610pressure.handle(self._boot_tgt)

    def test_050_sdp610pressure(self):
        """ Test the I2C device for LOCATION command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.sdp610pressure.handle(self._location)

    def test_051_sdp610pressure(self):
        """ Test the I2C device for CHAMBER_LED command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.sdp610pressure.handle(self._chamber_led)

    def test_052_sdp610pressure(self):
        """ Test the I2C device for LED command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.sdp610pressure.handle(self._led)

    def test_053_sdp610pressure(self):
        """ Test the I2C device for FAN command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.sdp610pressure.handle(self._fan)

    def test_054_sdp610pressure(self):
        """ Test the I2C device for HOST_INFO command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.sdp610pressure.handle(self._host_info)

    def test_055_sdp610pressure(self):
        """ Test the I2C device for RETRY command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.sdp610pressure.handle(self._retry)

    def test_056_sht31humidity(self):
        """ Test the RS485 device for VERSION command support.
        """
        self.sht31humidity.handle(self._version)

    def test_057_sht31humidity(self):
        """ Test the RS485 device for SCAN command support.
        """
        self.sht31humidity.handle(self._scan)

    def test_058_sht31humidity(self):
        """ Test the RS485 device for SCAN_ALL command support.
        """
        self.sht31humidity.handle(self._scan_all)

    def test_059_sht31humidity(self):
        """ Test the RS485 device for READ command support.
        """
        with self.assertRaises(KeyError):
            self.sht31humidity.handle(self._read)

    def test_060_sht31humidity(self):
        """ Test the RS485 device for WRITE command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.sht31humidity.handle(self._write)

    def test_061_sht31humidity(self):
        """ Test the RS485 device for POWER command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.sht31humidity.handle(self._power)

    def test_062_sht31humidity(self):
        """ Test the RS485 device for ASSET command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.sht31humidity.handle(self._asset)

    def test_063_sht31humidity(self):
        """ Test the RS485 device for BOOT_TARGET command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.sht31humidity.handle(self._boot_tgt)

    def test_064_sht31humidity(self):
        """ Test the RS485 device for LOCATION command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.sht31humidity.handle(self._location)

    def test_065_sht31humidity(self):
        """ Test the RS485 device for CHAMBER_LED command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.sht31humidity.handle(self._chamber_led)

    def test_066_sht31humidity(self):
        """ Test the RS485 device for LED command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.sht31humidity.handle(self._led)

    def test_067_sht31humidity(self):
        """ Test the RS485 device for FAN command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.sht31humidity.handle(self._fan)

    def test_068_sht31humidity(self):
        """ Test the RS485 device for HOST_INFO command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.sht31humidity.handle(self._retry)

    def test_069_sht31humidity(self):
        """ Test the RS485 device for RETRY command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.sht31humidity.handle(self._retry)

    def test_070_d6fw10a1airflow(self):
        """ Test the RS485 device for VERSION command support.
        """
        self.d6fw10a1airflow.handle(self._version)

    def test_071_d6fw10a1airflow(self):
        """ Test the RS485 device for SCAN command support.
        """
        self.d6fw10a1airflow.handle(self._scan)

    def test_072_d6fw10a1airflow(self):
        """ Test the RS485 device for SCAN_ALL command support.
        """
        self.d6fw10a1airflow.handle(self._scan_all)

    def test_073_d6fw10a1airflow(self):
        """ Test the RS485 device for READ command support.
        """
        with self.assertRaises(KeyError):
            self.d6fw10a1airflow.handle(self._read)

    def test_074_d6fw10a1airflow(self):
        """ Test the RS485 device for WRITE command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.d6fw10a1airflow.handle(self._write)

    def test_075_d6fw10a1airflow(self):
        """ Test the RS485 device for POWER command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.d6fw10a1airflow.handle(self._power)

    def test_076_d6fw10a1airflow(self):
        """ Test the RS485 device for ASSET command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.d6fw10a1airflow.handle(self._asset)

    def test_077_d6fw10a1airflow(self):
        """ Test the RS485 device for BOOT_TARGET command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.d6fw10a1airflow.handle(self._boot_tgt)

    def test_078_d6fw10a1airflow(self):
        """ Test the RS485 device for LOCATION command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.d6fw10a1airflow.handle(self._location)

    def test_079_d6fw10a1airflow(self):
        """ Test the RS485 device for CHAMBER_LED command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.d6fw10a1airflow.handle(self._chamber_led)

    def test_080_d6fw10a1airflow(self):
        """ Test the RS485 device for LED command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.d6fw10a1airflow.handle(self._led)

    def test_081_d6fw10a1airflow(self):
        """ Test the RS485 device for FAN command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.d6fw10a1airflow.handle(self._fan)

    def test_082_d6fw10a1airflow(self):
        """ Test the RS485 device for HOST_INFO command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.d6fw10a1airflow.handle(self._host_info)

    def test_083_d6fw10a1airflow(self):
        """ Test the RS485 device for RETRY command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.d6fw10a1airflow.handle(self._retry)

    def test_084_gs32010fan(self):
        """ Test the RS485 device for VERSION command support.
        """
        self.gs32010fan.handle(self._version)

    def test_085_gs32010fan(self):
        """ Test the RS485 device for SCAN command support.
        """
        self.gs32010fan.handle(self._scan)

    def test_086_gs32010fan(self):
        """ Test the RS485 device for SCAN_ALL command support.
        """
        self.gs32010fan.handle(self._scan_all)

    def test_087_gs32010fan(self):
        """ Test the RS485 device for READ command support.
        """
        with self.assertRaises(KeyError):
            self.gs32010fan.handle(self._read)

    def test_088_gs32010fan(self):
        """ Test the RS485 device for WRITE command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.gs32010fan.handle(self._write)

    def test_089_gs32010fan(self):
        """ Test the RS485 device for POWER command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.gs32010fan.handle(self._power)

    def test_090_gs32010fan(self):
        """ Test the RS485 device for ASSET command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.gs32010fan.handle(self._asset)

    def test_091_gs32010fan(self):
        """ Test the RS485 device for BOOT_TARGET command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.gs32010fan.handle(self._boot_tgt)

    def test_092_gs32010fan(self):
        """ Test the RS485 device for LOCATION command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.gs32010fan.handle(self._location)

    def test_093_gs32010fan(self):
        """ Test the RS485 device for CHAMBER_LED command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.gs32010fan.handle(self._chamber_led)

    def test_094_gs32010fan(self):
        """ Test the RS485 device for LED command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.gs32010fan.handle(self._led)

    def test_095_gs32010fan(self):
        """ Test the RS485 device for FAN command support.
        """
        with self.assertRaises(KeyError):
            self.gs32010fan.handle(self._fan)

    def test_096_gs32010fan(self):
        """ Test the RS485 device for HOST_INFO command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.gs32010fan.handle(self._host_info)

    def test_097_gs32010fan(self):
        """ Test the RS485 device for RETRY command support.
        """
        with self.assertRaises(CommandNotSupported):
            self.gs32010fan.handle(self._retry)
