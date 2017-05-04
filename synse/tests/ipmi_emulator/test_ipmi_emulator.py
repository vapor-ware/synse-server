#!/usr/bin/env python
""" Synse IPMI Emulator Tests

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
from pyghmi.ipmi.command import Command
from pyghmi.ipmi.sdr import SensorReading
from pyghmi.exceptions import IpmiException


class IPMIEmulatorTestCase(unittest.TestCase):
    """ Basic tests for the IPMI emulator - this uses the default built-in
    configuration for the IPMI emulator and just tests that pyghmi can properly
    connect and get data back from the emulator.
    """
    @classmethod
    def setUpClass(cls):
        cls.username = 'ADMIN'
        cls.password = 'ADMIN'
        cls.bmc = 'ipmi-emulator'
        cls.sensors = []

    def setUp(self):
        self.cmd = Command(
            bmc=self.bmc,
            userid=self.username,
            password=self.password,
            port=623
        )

    def tearDown(self):
        if self.cmd:
            self.cmd.ipmi_session.logout()

    def test_000_get_power(self):
        """ Test getting power status from the emulator.
        """
        res = self.cmd.get_power()
        self.assertIn('powerstate', res)
        self.assertEqual(res['powerstate'], 'on')

    def test_001_set_power(self):
        """ Test setting power status from the emulator. In this case, turn the power
        on even though it is already on.
        """
        res = self.cmd.set_power('on', wait=True)
        self.assertIn('powerstate', res)
        self.assertEqual(res['powerstate'], 'on')

    def test_002_get_power(self):
        """ Test getting power status from the emulator, which should still be 'on'
        """
        res = self.cmd.get_power()
        self.assertIn('powerstate', res)
        self.assertEqual(res['powerstate'], 'on')

    def test_003_set_power(self):
        """ Test setting power status from the emulator. In this case, turn the power
        off from an on state
        """
        res = self.cmd.set_power('off', wait=True)
        self.assertIn('powerstate', res)
        self.assertEqual(res['powerstate'], 'off')

    def test_004_get_power(self):
        """ Test getting power status from the emulator, which should now be 'off'
        """
        res = self.cmd.get_power()
        self.assertIn('powerstate', res)
        self.assertEqual(res['powerstate'], 'off')

    def test_005_get_sensor_descriptions(self):
        """ Test getting sensor descriptions from the BMC
        """
        res = self.cmd.get_sensor_descriptions()

        types = [
            'Voltage',
            'Fan',
            'Temperature',
            'Physical Security',
            'Power Supply'
        ]

        for item in res:
            self.assertIsInstance(item, dict)
            self.assertIn('type', item)
            self.assertIn('name', item)

            self.assertIn(item['type'], types)

    def test_006_get_sensor_numbers(self):
        """ Test getting sensor numbers from the BMC
        """
        # we will first want to initialize the SDR since it doesn't seem to do it on its own
        sdr = self.cmd.init_sdr()
        res = sdr.get_sensor_numbers()

        for item in res:
            self.assertIsInstance(item, int)
            self.assertIn(item, sdr.sensors)

            # for following tests, store the sensor name
            self.sensors.append(sdr.sensors[item].name)

    def test_007_read_sensor(self):
        """ Test reading a sensor from the emulator.

        At this point, the emulator's power is off, so we should get back readings
        of 0 for sensor reads.
        """
        self.assertGreater(len(self.sensors), 0)

        for sensor in self.sensors[:12]:
            with self.assertRaises(IpmiException):
                self.cmd.get_sensor_reading(sensor)

    def test_008_set_power(self):
        """ Test setting power status from the emulator. In this case, turn the power
        on from an off state
        """
        res = self.cmd.set_power('on', wait=True)
        self.assertIn('powerstate', res)
        self.assertEqual(res['powerstate'], 'on')

    def test_009_get_power(self):
        """ Test getting power status from the emulator, which should now be 'on'
        """
        res = self.cmd.get_power()
        self.assertIn('powerstate', res)
        self.assertEqual(res['powerstate'], 'on')

    def test_010_read_sensor(self):
        """ Test reading a sensor from the emulator.

        With the power back on, we should get sensor readings now. This sensor should
        have 5 values before it loops around again.
        """
        self.assertGreater(len(self.sensors), 0)
        sensor = self.sensors[0]

        for i in range(3):
            res = self.cmd.get_sensor_reading(sensor)
            self.assertIsInstance(res, SensorReading)
            self.assertAlmostEqual(res.value, 1.16, delta=0.0001)

            res = self.cmd.get_sensor_reading(sensor)
            self.assertIsInstance(res, SensorReading)
            self.assertAlmostEqual(res.value, 1.184, delta=0.0001)

            res = self.cmd.get_sensor_reading(sensor)
            self.assertIsInstance(res, SensorReading)
            self.assertAlmostEqual(res.value, 1.168, delta=0.0001)

            res = self.cmd.get_sensor_reading(sensor)
            self.assertIsInstance(res, SensorReading)
            self.assertAlmostEqual(res.value, 1.152, delta=0.0001)

            res = self.cmd.get_sensor_reading(sensor)
            self.assertIsInstance(res, SensorReading)
            self.assertAlmostEqual(res.value, 1.152, delta=0.0001)

    def test_011_read_sensor(self):
        """ Test reading a sensor from the emulator.

        This sensor should have 2 values before it loops around again.
        """
        self.assertGreater(len(self.sensors), 2)
        sensor = self.sensors[2]

        for i in range(3):
            res = self.cmd.get_sensor_reading(sensor)
            self.assertIsInstance(res, SensorReading)
            self.assertAlmostEqual(res.value, 3.28, delta=0.0001)

            res = self.cmd.get_sensor_reading(sensor)
            self.assertIsInstance(res, SensorReading)
            self.assertAlmostEqual(res.value, 3.216, delta=0.0001)

    def test_012_read_sensor(self):
        """ Test reading a sensor from the emulator.

        This sensor should have 1 value before it loops around again.
        """
        self.assertGreater(len(self.sensors), 4)
        sensor = self.sensors[4]

        for i in range(3):
            res = self.cmd.get_sensor_reading(sensor)
            self.assertIsInstance(res, SensorReading)
            self.assertAlmostEqual(res.value, 5.152, delta=0.0001)

    def test_013_get_boot(self):
        """ Test getting boot target
        """
        res = self.cmd.get_bootdev()

        self.assertIsInstance(res, dict)
        self.assertEqual(len(res), 3)
        self.assertIn('bootdev', res)
        self.assertIn('uefimode', res)
        self.assertIn('persistent', res)

        # we only care about boot target right now
        self.assertEqual(res['bootdev'], 'default')

    def test_014_set_boot(self):
        """ Test setting boot target to the value it already is set at.
        """
        res = self.cmd.set_bootdev('default')

        self.assertIsInstance(res, dict)
        self.assertEqual(len(res), 1)
        self.assertIn('bootdev', res)
        self.assertEqual(res['bootdev'], 'default')

    def test_015_get_boot(self):
        """ Test getting boot target, which should not have changed
        """
        res = self.cmd.get_bootdev()

        self.assertIsInstance(res, dict)
        self.assertEqual(len(res), 3)
        self.assertIn('bootdev', res)
        self.assertIn('uefimode', res)
        self.assertIn('persistent', res)

        # we only care about boot target right now
        self.assertEqual(res['bootdev'], 'default')

    def test_016_set_boot(self):
        """ Test setting boot target to a new value.
        """
        res = self.cmd.set_bootdev('hd')

        self.assertIsInstance(res, dict)
        self.assertEqual(len(res), 1)
        self.assertIn('bootdev', res)
        self.assertEqual(res['bootdev'], 'hd')

    def test_017_get_boot(self):
        """ Test getting boot target, which should now have changed
        """
        res = self.cmd.get_bootdev()

        self.assertIsInstance(res, dict)
        self.assertEqual(len(res), 3)
        self.assertIn('bootdev', res)
        self.assertIn('uefimode', res)
        self.assertIn('persistent', res)

        # we only care about boot target right now
        self.assertEqual(res['bootdev'], 'hd')

    def test_018_get_inventory(self):
        """ Test getting the inventory information from the FRU
        """
        res = self.cmd.get_inventory_of_component('System')

        self.assertIsInstance(res, dict)
        keys = [
            'board_extra', 'Manufacturer', 'Product ID', 'Board model',
            'UUID', 'oem_parser', 'Hardware Version', 'Manufacturer ID',
            'Board product name', 'Board manufacturer', 'Device Revision',
            'Serial Number', 'Product name', 'Asset Number', 'Device ID',
            'Model', 'Board manufacture date', 'Board serial number',
            'product_extra'
        ]
        for k in keys:
            self.assertIn(k, res)

    def test_019_get_identify(self):
        """ Retrieve the remote system LED status
        """
        res = self.cmd.raw_command(netfn=0, command=1, data=[])

        # here, we expect the raw response back, so need to make sure it
        # matches with what is expected
        self.assertIn('command', res)
        self.assertEqual(res['command'], 1)

        self.assertIn('code', res)
        self.assertEqual(res['code'], 0)

        self.assertIn('netfn', res)
        self.assertEqual(res['netfn'], 1)

        self.assertIn('data', res)
        self.assertIsInstance(res['data'], list)
        # validate that the LED is on
        self.assertFalse((res['data'][2] >> 5) & 0x01 or (res['data'][2] >> 4) & 0x01)

    def test_020_set_identify(self):
        """ Set the remote system LED status, here we set it to the same state it is
        already in.
        """
        # this will not have a return, so we expect 'None' - the effect
        # of this command is tested in the next test method
        res = self.cmd.set_identify(on=False)
        self.assertEqual(res, None)

    def test_021_get_identify(self):
        """ Retrieve the remote system LED status, here is should be the same.
        """
        res = self.cmd.raw_command(netfn=0, command=1, data=[])

        # here, we expect the raw response back, so need to make sure it
        # matches with what is expected
        self.assertIn('command', res)
        self.assertEqual(res['command'], 1)

        self.assertIn('code', res)
        self.assertEqual(res['code'], 0)

        self.assertIn('netfn', res)
        self.assertEqual(res['netfn'], 1)

        self.assertIn('data', res)
        self.assertIsInstance(res['data'], list)
        # validate that the LED is on
        self.assertFalse((res['data'][2] >> 5) & 0x01 or (res['data'][2] >> 4) & 0x01)

    def test_022_set_identify(self):
        """ Set the remote system LED status, here we set it to a new state.
        """
        # this will not have a return, so we expect 'None' - the effect
        # of this command is tested in the next test method
        res = self.cmd.set_identify(on=True)
        self.assertEqual(res, None)

    def test_023_get_identify(self):
        """ Retrieve the remote system LED status, now it should have changed.
        """
        res = self.cmd.raw_command(netfn=0, command=1, data=[])

        # here, we expect the raw response back, so need to make sure it
        # matches with what is expected
        self.assertIn('command', res)
        self.assertEqual(res['command'], 1)

        self.assertIn('code', res)
        self.assertEqual(res['code'], 0)

        self.assertIn('netfn', res)
        self.assertEqual(res['netfn'], 1)

        self.assertIn('data', res)
        self.assertIsInstance(res['data'], list)
        # validate that the LED is on
        self.assertTrue((res['data'][2] >> 5) & 0x01 or (res['data'][2] >> 4) & 0x01)

    def test_024_get_dcmi_power_reading(self):
        """ Get a DCMI power reading.
        """
        res = self.cmd.raw_command(netfn=0x2c, command=0x02, data=(0xdc, 0x01, 0x00, 0x00))

        # here, we expect the raw response back, so need to make sure it
        # matches with what is expected
        self.assertIn('command', res)
        self.assertEqual(res['command'], 0x02)

        self.assertIn('code', res)
        self.assertEqual(res['code'], 0x00)

        self.assertIn('netfn', res)
        self.assertEqual(res['netfn'], 0x2d)

        self.assertIn('data', res)
        self.assertIsInstance(res['data'], list)

        # Here we will only check the current, min, max and avg.
        # There is slop in the current watts since the emulator emits different
        # results for each client call. Just check that we get something in the
        # min / max range.
        self.assertTrue(0x96 <= res['data'][1] <= 0xFA)  # Current watts low byte. 150 <= reading <=250.
        self.assertEqual(res['data'][2], 0x00)  # Current watts high byte.
        self.assertEqual(res['data'][3:5], [0x96, 0x00])  # min watts
        self.assertEqual(res['data'][5:7], [0xfa, 0x00])  # max watts
        self.assertEqual(res['data'][7:9], [0xc8, 0x00])  # avg watts

    def test_025_get_dcmi_general_capabilities(self):
        """ Get DCMI capabilities for general capabilities support parameter (0x01).
        """
        res = self.cmd.raw_command(netfn=0x2c, command=0x01, data=(0xdc, 0x01))

        # here, we expect the raw response back, so need to make sure it
        # matches with what is expected
        self.assertIn('command', res)
        self.assertEqual(res['command'], 0x01)

        self.assertIn('code', res)
        self.assertEqual(res['code'], 0x00)

        self.assertIn('netfn', res)
        self.assertEqual(res['netfn'], 0x2d)

        self.assertIn('data', res)
        self.assertIsInstance(res['data'], list)

        # check the response bytes for parameter 1
        self.assertEqual(res['data'][0:4], [0xdc, 0x01, 0x05, 0x02])  # dcmi 1.5 param rev 02
        self.assertEqual(res['data'][4:7], [0x00, 0x01, 0x07])  # reserved, power enabled, all mgt cap enabled

    def test_026_get_dcmi_mandatory_capabilities(self):
        """ Get DCMI capabilities for mandatory capabilities support parameter (0x02).
        """
        res = self.cmd.raw_command(netfn=0x2c, command=0x01, data=(0xdc, 0x02))

        # here, we expect the raw response back, so need to make sure it
        # matches with what is expected
        self.assertIn('command', res)
        self.assertEqual(res['command'], 0x01)

        self.assertIn('code', res)
        self.assertEqual(res['code'], 0x00)

        self.assertIn('netfn', res)
        self.assertEqual(res['netfn'], 0x2d)

        self.assertIn('data', res)
        self.assertIsInstance(res['data'], list)

        # check the response bytes for parameter 2
        self.assertEqual(res['data'][0:4], [0xdc, 0x01, 0x05, 0x02])        # dcmi 1.5 param rev 02
        self.assertEqual(res['data'][4:9], [0x00, 0x00, 0x00, 0x00, 0x00])  # nothing supported for now (ignored)

    def test_027_get_dcmi_optional_capabilities(self):
        """ Get DCMI capabilities for optional capabilities support parameter (0x03).
        """
        res = self.cmd.raw_command(netfn=0x2c, command=0x01, data=(0xdc, 0x03))

        # here, we expect the raw response back, so need to make sure it
        # matches with what is expected
        self.assertIn('command', res)
        self.assertEqual(res['command'], 0x01)

        self.assertIn('code', res)
        self.assertEqual(res['code'], 0x00)

        self.assertIn('netfn', res)
        self.assertEqual(res['netfn'], 0x2d)

        self.assertIn('data', res)
        self.assertIsInstance(res['data'], list)

        # check the response bytes for parameter 3
        self.assertEqual(res['data'][0:4], [0xdc, 0x01, 0x05, 0x02])    # dcmi 1.5 param rev 02
        self.assertEqual(res['data'][4:7], [0x20, 0x00])                # 0x20=BMC, primary/rev0

    def test_028_get_dcmi_mgmt_capabilities(self):
        """ Get DCMI capabilities for management controller addresses parameter (0x04).
        """
        res = self.cmd.raw_command(netfn=0x2c, command=0x01, data=(0xdc, 0x04))

        # here, we expect the raw response back, so need to make sure it
        # matches with what is expected
        self.assertIn('command', res)
        self.assertEqual(res['command'], 0x01)

        self.assertIn('code', res)
        self.assertEqual(res['code'], 0x00)

        self.assertIn('netfn', res)
        self.assertEqual(res['netfn'], 0x2d)

        self.assertIn('data', res)
        self.assertIsInstance(res['data'], list)

        # check the response bytes for parameter 4
        self.assertEqual(res['data'][0:4], [0xdc, 0x01, 0x05, 0x02])    # dcmi 1.5 param rev 02
        self.assertEqual(res['data'][4:7], [0xff, 0xff, 0xff])          # 0xff - nothing supported (ignored)

    def test_029_get_dcmi_enhanced_power_capabilities(self):
        """ Get DCMI capabilities for enhanced power parameter (0x05).
        """
        res = self.cmd.raw_command(netfn=0x2c, command=0x01, data=(0xdc, 0x05))

        # here, we expect the raw response back, so need to make sure it
        # matches with what is expected
        self.assertIn('command', res)
        self.assertEqual(res['command'], 0x01)

        self.assertIn('code', res)
        self.assertEqual(res['code'], 0x00)

        self.assertIn('netfn', res)
        self.assertEqual(res['netfn'], 0x2d)

        self.assertIn('data', res)
        self.assertIsInstance(res['data'], list)

        # check the response bytes for parameter 5
        self.assertEqual(res['data'][0:4], [0xdc, 0x01, 0x05, 0x02])    # dcmi 1.5 param rev 02
        self.assertEqual(res['data'][4:6], [0x01, 0x00])                # 0x01 - 1 avg period, 0x00 "now"

    def test_030_get_dcmi_bad_capabilities(self):
        """ Get DCMI capabilities where the parameter selector is invalid, so we timeout.
            (IRL, there would likely be a proper IPMI error returned here, but we can at least test timout here).
        """
        res = self.cmd.raw_command(netfn=0x2c, command=0x01, data=(0xdc, 0x06))

        # for now we expect a timeout error, with code of 65535 (0xffff)
        self.assertIn('error', res)
        self.assertEqual(res['error'], 'timeout')

        self.assertIn('code', res)
        self.assertEqual(res['code'], 0xffff)
