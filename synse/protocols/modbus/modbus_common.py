#!/usr/bin/env python
"""
        \\//
         \/apor IO


-------------------------------
Copyright (C) 2015-18  Vapor IO

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

# pylint: disable=import-error

import logging
import struct
from synse.protocols.modbus import dkmodbus  # nopep8
from synse.protocols.conversions import conversions  # nopep8

logger = logging.getLogger(__name__)


def get_fan_direction_ecblue(ser, slave_address):
    """Production only direction reads from ECblue fan (vapor_fan).
    :param ser: Serial connection to the fan controller.
    :param slave_address: The Modbus slave address of the device.
    :return: The fan direction of forward or reverse.
    """
    direction = read_holding_register(ser, slave_address, 1)
    direction &= 8
    if direction == 0:
        return 'forward'
    return 'reverse'


def get_fan_direction_gs3(ser, slave_address):
    """Get the current fan direction for a gs3 fan controller.
    :param ser: Serial connection to the gs3 fan controller.
    :param slave_address: The Modbus slave address of the device.
    :return: The fan direction of forward or reverse.
    """
    direction = read_holding_register(ser, slave_address, 0x91C)
    if direction == 0:
        return 'forward'
    elif direction == 1:
        return 'reverse'
    else:
        raise ValueError('Unknown direction {}'.format(direction))


def get_fan_frequency_gs3(ser, slave_address):
    """Get the base (max) frequency of the fan motor through the gs3 fan
    controller.
    :param ser: Serial connection to the gs3 fan controller.
    :param slave_address: The Modbus slave address of the device.
    :returns: The base motor frequency.
    """
    return read_holding_register(ser, slave_address, 0x0002)


def get_fan_rpm_ecblue(ser, slave_address):
    """Production only rpm reads from ECblue fan (vapor_fan).
    :param ser: Serial connection to the ECblue fan controller.
    :param slave_address: The Modbus slave address of the device.
    :return: The fan speed in rpm.
    """
    # TODO: There may be another register for this.
    # We are reading off of the Hz setting and there is going to be ramp up/down
    # time which is not taken into account here.
    max_rpm = get_fan_max_rpm_ecblue(ser, slave_address)
    logger.debug('max_rpm: {}'.format(max_rpm))

    # Get the hz setting in Hz * 10.
    hz_setting = read_holding_register(ser, slave_address, 0x02)
    logger.debug('raw Hz setting: 0x{:04x}'.format(hz_setting))
    # Convert from hex to BCD.
    hz_setting_string = '{:04x}'.format(hz_setting)
    hz_setting_int = int(hz_setting_string)
    hz_setting_float = float(hz_setting_int) / 10.0
    ratio = hz_setting_float / 60.0
    rpm = int(max_rpm * ratio)
    logger.debug('rpm: {}'.format(rpm))
    return rpm


def get_fan_rpm_gs3(ser, slave_address):
    """Get the current fan rpm for a gs3 fan controller.
    :param ser: Serial connection to the gs3 fan controller.
    :param slave_address: The Modbus slave address of the device.
    :return: The fan speed in rpm.
    """
    return read_holding_register(ser, slave_address, 0x2107)


def get_fan_rpm_to_hz_gs3(ser, slave_address, max_rpm):
    """Get the conversion from rpm to hertz. The operator sets the fan speed in
    rpm. The fan controller sets the fan speed in hertz.
    :param ser: Serial connection to the gs3 fan controller.
    :param slave_address: The Modbus slave address of the device.
    :param max_rpm: The maximum rpm of the fan motor.
    :returns: The conversion from rpm to hertz.
    """
    base_frequency = get_fan_frequency_gs3(ser, slave_address)
    return float(base_frequency) / float(max_rpm)


def get_fan_max_rpm_ecblue(ser, slave_address):
    """Get the maximum rpm of the fan motor through the ECblue fan controller.
    :param ser: Serial connection to the ECblue fan controller.
    :param slave_address: The Modbus slave address of the device.
    :returns: The base maximum rpm of the fan motor.
    """
    return read_holding_register(ser, slave_address, 0x08)


def get_fan_max_rpm_gs3(ser, slave_address):
    """Get the maximum rpm of the fan motor through the gs3 fan controller.
    :param ser: Serial connection to the gs3 fan controller.
    :param slave_address: The Modbus slave address of the device.
    :returns: The base maximum rpm of the fan motor.
    """
    return read_holding_register(ser, slave_address, 0x0004)


def read_holding_register(ser, slave_address, register):
    """Read a holding register from an RS485 device.
    :param ser: Serial connection to the fan controller.
    Contains baud rate, parity, and timeout.
    :param slave_address: The Modbus slave address of the device.
    :param register: The register to read (int).
    :returns The register reading (int).
    """
    client = dkmodbus.dkmodbus(ser)
    register_data = client.read_holding_registers(slave_address, register, 1)
    result = unpack_register_data(register_data)
    logger.debug('read_holding_register result: {}, type: {}'.format(result, type(result)))
    return result


def read_input_register(ser, slave_address, register):
    """Read an input register from an RS485 device.
    :param ser: Serial connection to the fan controller.
    Contains baud rate, parity, and timeout.
    :param slave_address: The Modbus slave address of the device.
    :param register: The register to read (int).
    :returns The register reading (int).
    """
    client = dkmodbus.dkmodbus(ser)
    register_data = client.read_input_registers(slave_address, register, 1)
    logger.debug('input register_data (raw): {} length: {}'.format(
        register_data, len(register_data)))
    result = unpack_register_data(register_data)
    logger.debug('read_input_register result: 0x{}'.format(result))
    return result


def set_fan_rpm_ecblue(ser, slave_address, rpm_setting, max_rpm):
    """
    Set the fan speed in rpm on an ECblue fan controller.
    :param ser: Serial connection to the gs3 fan controller.
    Contains baud rate, parity, and timeout.
    :param slave_address: The Modbus slave address of the device.
    :param rpm_setting: The user supplied rpm setting.
    :param max_rpm: The max rpm setting for the fan motor.
    :return: The modbus write result.
    """
    client = dkmodbus.dkmodbus(ser)

    logger.debug('Setting fan speed. max_rpm: {}, rpm_setting: {}'.format(
        max_rpm, rpm_setting))

    percentage_setting = float(rpm_setting) / float(max_rpm)
    logger.debug('percentage_setting: {}'.format(percentage_setting))
    fan_setting_decimal = int(percentage_setting * float(600.0))
    logger.debug('fan_setting_decimal: {}d 0x{:04x}'.format(
        fan_setting_decimal, fan_setting_decimal))

    fan_setting = (fan_setting_decimal / 100) << 8
    logger.debug('fan_setting: {}d 0x{}'.format(fan_setting, fan_setting))
    setting = ((fan_setting_decimal % 100) / 10) << 4
    fan_setting += setting
    logger.debug('fan_setting: {}d 0x{}'.format(fan_setting, fan_setting))
    setting = (fan_setting_decimal % 10)
    fan_setting += setting
    logger.debug('fan_setting: {}d 0x{}'.format(fan_setting, fan_setting))

    fan_setting = struct.pack('>H', fan_setting)

    result = client.write_multiple_registers(
        slave_address,  # Slave address.
        2,  # Register to write to.
        1,  # Number of registers to write to.
        2,  # Number of bytes to write.
        fan_setting)  # Data to write.
    return result


def set_fan_rpm_gs3(ser, slave_address, rpm_setting, max_rpm):
    """
    Set the fan speed in rpm on a gs3 fan controller.
    :param ser: Serial connection to the gs3 fan controller.
    Contains baud rate, parity, and timeout.
    :param slave_address: The Modbus slave address of the device.
    :param rpm_setting: The user supplied rpm setting.
    :param max_rpm: The max rpm setting for the fan motor.
    :return: The modbus write result.
    """
    client = dkmodbus.dkmodbus(ser)
    if rpm_setting == 0:  # Turn the fan off.
        result = client.write_multiple_registers(
            slave_address,  # Slave address.
            0x91B,  # Register to write to.
            1,  # Number of registers to write to.
            2,  # Number of bytes to write.
            '\x00\x00')  # Data to write.
    else:  # Turn the fan on at the desired RPM.
        rpm_to_hz = get_fan_rpm_to_hz_gs3(
            client.serial_device, slave_address, max_rpm)
        hz = rpm_setting * rpm_to_hz
        packed_hz = conversions.fan_gs3_packed_hz(hz)

        result = client.write_multiple_registers(
            1,  # Slave address.
            0x91A,  # Register to write to.
            2,  # Number of registers to write to.
            4,  # Number of bytes to write.
            packed_hz + '\x00\x01')  # Frequency setting in Hz / data # 01 is on, # 00 is off.
    return result


def unpack_register_data(register_data):
    """
    Unpacks register_data from a byte string to int.
    :param register_data: The data to unpack.
    :return: The data as an int.
    """
    length = len(register_data)
    if length == 2:
        return conversions.unpack_word(register_data)
    elif length == 1:
        return conversions.unpack_byte(register_data)
    else:
        raise ValueError('Unexpected length {}.'.format(length))
