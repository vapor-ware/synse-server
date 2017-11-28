#!/usr/bin/env python
"""
        \\//
         \/apor IO


        Common file for modbus operations to avoid cut and paste.
        The gs3 command line tool and the synse device bus use this code.
"""

import logging
import struct
from synse.protocols.modbus import dkmodbus  # nopep8
from synse.protocols.conversions import conversions  # nopep8

logger = logging.getLogger(__name__)


def get_fan_direction_ebmpapst(ser, slave_address):
    """Production only direction reads from Ebm Papst fan (vapor_fan).
    :param ser: Serial connection to the fan controller.
    :param slave_address: The Modbus slave address of the device.
    :return: The fan direction of forward or reverse.
    """
    direction = read_input_register(ser, slave_address, 0xD018)
    if direction == 0:
        # TODO: This is counter-clockwise. (When viewed how? Unclear.)
        return 'forward'
    elif direction == 1:
        # TODO: This is clockwise.
        return 'reverse'
    else:
        raise ValueError('Unknown direction {}'.format(direction))


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


def get_fan_rpm_ebmpapst(ser, slave_address):
    """Production only rpm reads from Ebm Papst fan (vapor_fan).
    :param ser: Serial connection to the gs3 fan controller.
    :param slave_address: The Modbus slave address of the device.
    :return: The fan speed in rpm.
    """
    # TODO: Validate register and conversion.
    max_rpm = get_fan_max_rpm_ebmpapst(ser, slave_address)
    result = read_input_register(ser, slave_address, 0xD010)
    rpm = result * max_rpm / 64000
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


def get_fan_max_rpm_ebmpapst(ser, slave_address):
    """Get the maximum rpm of the fan motor through the ebm fan controller.
    :param ser: Serial connection to the ebm fan controller.
    :param slave_address: The Modbus slave address of the device.
    :returns: The base maximum rpm of the fan motor.
    """
    # TODO: Validate register and base (10 or 16).
    return read_holding_register(ser, slave_address, 0xD119)


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
    result = conversions.unpack_word(register_data)
    logger.debug('0x{}'.format(result))
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
    result = conversions.unpack_word(register_data)
    logger.debug('0x{}'.format(result))
    return result


def set_fan_rpm_ebmpapst(ser, slave_address, rpm_setting, max_rpm):
    """
    Set the fan speed in rpm on an ebmpapst fan controller.
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
    fan_setting = int(percentage_setting * float(0xFFFF))
    logger.debug('fan_setting: {}'.format(fan_setting))

    fan_setting = struct.pack('>H', fan_setting)

    # TODO: Find out if we need to write a password first.

    result = client.write_multiple_registers(
        slave_address,  # Slave address.
        0xD001,  # Register to write to.
        1,  # Number of registers to write to.
        2,  # Number of bytes to write.
        fan_setting)  # Data to write.

    # TODO: We may need a reset here which is _really_ odd.

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
