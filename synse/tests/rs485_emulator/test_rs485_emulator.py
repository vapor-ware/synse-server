#!/usr/bin/env python
""" Synse RS485 Emulator Tests

    Author: Andrew Cencini
    Date:   10/11/2016
    
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

from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from synse.tests.test_config import RS485_TEST_CLIENT_DEVICE, RS485_TEST_TIMEOUT_SEC


class Rs485EmulatorTestCase(unittest.TestCase):
    """ Basic tests for the RS485 emulator - uses a simple config with multiple units hanging off of it
    for different test cases.  Verifies that the pymodbus client can connect and send and receive data to/from
    the emulator.
    """
    def test_001_connect(self):
        """ verify that we can connect to the test device
        """
        with ModbusClient(method='rtu', port=RS485_TEST_CLIENT_DEVICE, timeout=RS485_TEST_TIMEOUT_SEC) as client:
            self.assertTrue(client.connect())

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # device (unit) tests (device: 0x01..0x0a)
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def test_002_good_device_register_read(self):
        """ read register 0 from good device -> good result, read repeatedly, read from multiple good devices
        """
        with ModbusClient(method='rtu', port=RS485_TEST_CLIENT_DEVICE, timeout=RS485_TEST_TIMEOUT_SEC) as client:
            self.assertTrue(client.connect())

            for device_address in range(0x01, 0x0b):
                result = client.read_holding_registers(0, count=1, unit=device_address)
                self.assertIsNotNone(result)
                self.assertEqual(result.registers[0], 0xBB00 + device_address)

    def test_003_bad_device_register_read(self):
        """ read register 0 from bad device -> bad result, read repeatedly, try multiple bad devices
        """
        with ModbusClient(method='rtu', port=RS485_TEST_CLIENT_DEVICE, timeout=RS485_TEST_TIMEOUT_SEC) as client:
            self.assertTrue(client.connect())

            for device_address in range(0xb0, 0xbb):
                result = client.read_holding_registers(0, count=1, unit=device_address)
                self.assertIsNotNone(result)
                self.assertGreaterEqual(result.function_code, 0x80)

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # register tests (device: 0x0b, good registers 0x0000..0x000a, 0x0010, 0x0bee, 0x7ac0)
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def test_004_good_register_single_read(self):
        """ read good register from good device -> good result, read for different good registers
        """
        with ModbusClient(method='rtu', port=RS485_TEST_CLIENT_DEVICE, timeout=RS485_TEST_TIMEOUT_SEC) as client:
            self.assertTrue(client.connect())

            for register in range(0x00, 0x0b):
                result = client.read_holding_registers(register, count=1, unit=0x0b)
                self.assertIsNotNone(result)
                self.assertEqual(result.registers[0], 0xcc00 + register)

            i = 1
            for register in [0x0010, 0x0bee, 0x7ac0]:
                result = client.read_holding_registers(register, count=1, unit=0x0b)
                self.assertIsNotNone(result)
                self.assertEqual(result.registers[0], 0xcd00 + i)
                i += 1

    def test_005_bad_register_single_read(self):
        """ read bad register from good device -> bad result, read multiple bad registers
        """
        with ModbusClient(method='rtu', port=RS485_TEST_CLIENT_DEVICE, timeout=RS485_TEST_TIMEOUT_SEC) as client:
            self.assertTrue(client.connect())

            for register in range(0x15, 0x1f):
                result = client.read_holding_registers(register, count=1, unit=0x0b)
                self.assertIsNotNone(result)
                # illegal data address
                self.assertEqual(result.exception_code, 2)

            for register in [0x0011, 0x0bff, 0x7ac1]:
                result = client.read_holding_registers(register, count=1, unit=0x0b)
                self.assertIsNotNone(result)
                # illegal data address
                self.assertEqual(result.exception_code, 2)

    def test_006_good_register_multi_read(self):
        """ read good register plus valid count -> good result, read for different valid counts
        """
        with ModbusClient(method='rtu', port=RS485_TEST_CLIENT_DEVICE, timeout=RS485_TEST_TIMEOUT_SEC) as client:
            self.assertTrue(client.connect())

            for register in range(0x00, 0x0b):
                # hit all neighborly registers
                for count in range(0x01, 0x0c - register):
                    result = client.read_holding_registers(register, count=count, unit=0x0b)
                    self.assertIsNotNone(result)
                    self.assertEqual(len(result.registers), count)
                    self.assertEqual(result.registers, [0xcc00 + register + x for x in range(0, count)])

    def test_007_good_register_bad_multi_read(self):
        """ read good register plus invalid count -> bad result, read for different invalid counts
        """
        with ModbusClient(method='rtu', port=RS485_TEST_CLIENT_DEVICE, timeout=RS485_TEST_TIMEOUT_SEC) as client:
            self.assertTrue(client.connect())

            for register in range(0x00, 0x0b):
                result = client.read_holding_registers(register, count=0x0c, unit=0x0b)
                self.assertIsNotNone(result)
                # illegal data address
                self.assertEqual(result.exception_code, 2)

                result = client.read_holding_registers(register, count=0x00, unit=0x0b)
                self.assertIsNotNone(result)
                # illegal data value
                self.assertEqual(result.exception_code, 3)

                result = client.read_holding_registers(register, count=0xf6, unit=0x0b)
                self.assertIsNotNone(result)
                # illegal data value
                self.assertEqual(result.exception_code, 3)

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # write tests (device: 0x0c, good registers 0x0000..0x000a, 0x0010, 0x0bee, 0x7ac0)
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def test_008_good_register_single_write(self):
        """ write good register, single value -> good result, for different good registers
        """
        with ModbusClient(method='rtu', port=RS485_TEST_CLIENT_DEVICE, timeout=RS485_TEST_TIMEOUT_SEC) as client:
            self.assertTrue(client.connect())

            for register in range(0x00, 0x0b):
                result = client.read_holding_registers(register, 1, unit=0x0c)
                self.assertIsNotNone(result)
                self.assertEqual(result.registers[0], 0xcc00 + register)

                result = client.write_registers(register, [0xdd00 + register], unit=0x0c)
                self.assertIsNotNone(result)
                self.assertLess(result.function_code, 0x80)

                result = client.read_holding_registers(register, 1, unit=0x0c)
                self.assertIsNotNone(result)
                self.assertEqual(result.registers[0], 0xdd00 + register)

            i = 1
            for register in [0x0010, 0x0bee, 0x7ac0]:
                result = client.read_holding_registers(register, 1, unit=0x0c)
                self.assertIsNotNone(result)
                self.assertEqual(result.registers[0], 0xcd00 + i)

                result = client.write_registers(register, [0xdc00 + i], unit=0x0c)
                self.assertIsNotNone(result)
                self.assertLess(result.function_code, 0x80)

                result = client.read_holding_registers(register, 1, unit=0x0c)
                self.assertIsNotNone(result)
                self.assertEqual(result.registers[0], 0xdc00 + i)
                i += 1

    def test_009_bad_register_single_write(self):
        """ write bad register, single value -> bad result, for different bad registers
        """
        with ModbusClient(method='rtu', port=RS485_TEST_CLIENT_DEVICE, timeout=RS485_TEST_TIMEOUT_SEC) as client:
            self.assertTrue(client.connect())

            for register in range(0x15, 0x1f):
                result = client.write_registers(register, [1], unit=0x0c)
                self.assertIsNotNone(result)
                # illegal address
                self.assertEqual(result.exception_code, 2)

            for register in [0x0011, 0x0bff, 0x7ac1]:
                result = client.write_registers(register, [1], unit=0x0c)
                self.assertIsNotNone(result)
                # illegal address
                self.assertEqual(result.exception_code, 2)

    def test_010_good_register_multi_write(self):
        """ write good register, multiple values -> good result, for different good registers
        """
        with ModbusClient(method='rtu', port=RS485_TEST_CLIENT_DEVICE, timeout=RS485_TEST_TIMEOUT_SEC) as client:
            self.assertTrue(client.connect())

            for register in range(0x00, 0x0b):
                # hit all neighborly registers
                for count in range(0x01, 0x0c - register):
                    result = client.write_registers(register, [0xee00+x for x in range(1, count+1)], unit=0x0c)
                    self.assertIsNotNone(result)
                    self.assertLess(result.function_code, 0x80)

                    result = client.read_holding_registers(register, count, unit=0x0c)
                    self.assertIsNotNone(result)
                    self.assertEqual(len(result.registers), count)
                    self.assertEqual(result.registers, [0xee00+x for x in range(1, count+1)])

    def test_011_good_register_bad_multi_write(self):
        """ write good register, multiple values but count too large -> bad result, for different bad counts
        """
        with ModbusClient(method='rtu', port=RS485_TEST_CLIENT_DEVICE, timeout=RS485_TEST_TIMEOUT_SEC) as client:
            self.assertTrue(client.connect())

            for register in range(0x00, 0x0b):
                result = client.write_registers(register, range(0x00, 0x0c), unit=0x0c)
                self.assertIsNotNone(result)
                self.assertGreaterEqual(result.function_code, 0x80)

                with self.assertRaises(Exception):
                    client.read_holding_registers(register, [], unit=0x0c)

                with self.assertRaises(Exception):
                    client.read_holding_registers(register, range(0x00, 0xf7), unit=0x0c)

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # cycle tests (device: 0x0d, good registers 0x0000..0x000a, 0x0010, 0x0bee, 0x7ac0)
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    def test_012_read_single_cyclic_register_good(self):
        """ repeatedly read from register that cycles through values -> good result, valid values
        """
        with ModbusClient(method='rtu', port=RS485_TEST_CLIENT_DEVICE, timeout=RS485_TEST_TIMEOUT_SEC) as client:
            self.assertTrue(client.connect())

            for i in range(0, 10):
                result = client.read_holding_registers(0x00, count=1, unit=0x0d)
                self.assertIsNotNone(result)
                self.assertEqual(result.registers[0], 0xee00 + (i % 4))

    def test_013_read_multiple_cyclic_registers_good(self):
        """ repeatedly read from register that cycles through values, count of multiple -> good result, valid values
        """
        with ModbusClient(method='rtu', port=RS485_TEST_CLIENT_DEVICE, timeout=RS485_TEST_TIMEOUT_SEC) as client:
            self.assertTrue(client.connect())

            for i in range(1, 5):
                result = client.read_holding_registers(i, count=1, unit=0x0d)
                self.assertIsNotNone(result)
                self.assertEqual(result.registers[0], [0x00aa, 0x00bb, 0x00cc, 0x00dd][i-1])

            for i in range(1, 5):
                result = client.read_holding_registers(i, count=1, unit=0x0d)
                self.assertIsNotNone(result)
                self.assertEqual(result.registers[0], [0x00aa, 0x00bb, 0xcccc, 0x00dd][i-1])

            for i in range(1, 5):
                result = client.read_holding_registers(i, count=1, unit=0x0d)
                self.assertIsNotNone(result)
                self.assertEqual(result.registers[0], [0x00aa, 0x00bb, 0x00cc, 0x00dd][i-1])

    def test_014_multiread_multiple_cyclic_registers_good(self):
        """ repeatedly read from register that cycles through values, count of multiple -> good result, valid values
        """
        with ModbusClient(method='rtu', port=RS485_TEST_CLIENT_DEVICE, timeout=RS485_TEST_TIMEOUT_SEC) as client:
            self.assertTrue(client.connect())

            result = client.read_holding_registers(0x0001, count=4, unit=0x0d)
            self.assertIsNotNone(result)
            self.assertEqual(result.registers, [0x00aa, 0x00bb, 0xcccc, 0x00dd])

            result = client.read_holding_registers(0x0001, count=4, unit=0x0d)
            self.assertIsNotNone(result)
            self.assertEqual(result.registers, [0x00aa, 0x00bb, 0x00cc, 0x00dd])

            result = client.read_holding_registers(0x0001, count=4, unit=0x0d)
            self.assertIsNotNone(result)
            self.assertEqual(result.registers, [0x00aa, 0x00bb, 0xcccc, 0x00dd])


    # future - readwrite?
