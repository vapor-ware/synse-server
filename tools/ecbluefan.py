#!/usr/bin/env python

""" Run this off the command line by:
sudo -HE env PATH=$PATH ./ecbluefan.py get

Command line tool for the ECblue fan controller.
"""

import sys
import os
import serial
import logging
import struct
import time

# before we import the synse protocol packages, we want to make sure it
# is reachable on the pythonpath
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from synse.protocols.modbus import dkmodbus  # nopep8
from synse.protocols.modbus import modbus_common  # nopep8

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed packet traces.

# Default Modbus slave address for the fan controller.
FAN_SLAVE_ADDRESS = 1

# Fan controller holding registers. Key is the register address. Value is the description.
FAN_HOLDING_REGISTERS = {

    # Control

    0x00: 'PIN input',
    0x01: 'Control',
    0x02: 'Speed control',
    0x03: 'COM Parameter',
    0x04: 'Controlmode',
    0x05: 'Set Intern1',
    0x06: 'Set Intern2: 1/min',
    0x07: 'Min. Speed: 1/min',
    0x08: 'Max. Speed: 1/min',
    0x09: 'Set Intern3: 1/min',

    # I/O Setup

    0x10: 'Inverting',
    0x11: 'E11 Min',
    0x12: 'E12 Max',
    0x13: 'E1 Function',
    0x14: 'D1 Function',
    0x15: 'K1 Function',
    0x16: 'Controller Setup Flags',
    0x17: 'communication / control signal watchdog',
    0x18: 'Limit',
    0x19: 'Radio network code',

    # Motor Setup

    0x20: 'Non-doc 0x20',
    0x21: 'Non-doc 0x21',
    0x22: 'Non-doc 0x22',
    0x23: 'Non-doc 0x23',
    0x24: 'Non-doc 0x24',

    0x25: 'Ramp timing',

    0x26: 'Non-doc 0x26',
    0x27: 'Non-doc 0x27',
    0x28: 'Non-doc 0x28',
    0x29: 'Non-doc 0x29',

    # Speed range suppression

    0x30: 'Suppression',
    0x31: 'Range1 Min',

    # These may only be returning one byte, not 2.
    0x32: 'Bereich1 Max',  # Bereich is Area
    0x33: 'Range2 Min',
    0x34: 'Rereich2 Max',  # Guessing Rereich is a typo (?)
    0x35: 'Range3 Min',
    0x36: 'Rereich3 Max',
    0x37: 'Fan Bad',

    0x38: 'Non-doc 0x38',
    0x39: 'Non-doc 0x39',

    0x40: 'Non-doc 0x40',
    0x41: 'Non-doc 0x41',
    0x42: 'Non-doc 0x42',
    0x43: 'Non-doc 0x43',
    0x44: 'Non-doc 0x44',
    0x45: 'Non-doc 0x45',
    0x46: 'Non-doc 0x46',
    0x47: 'Non-doc 0x47',
    0x48: 'Non-doc 0x48',
    0x49: 'Non-doc 0x49',

}

# Fan controller input registers. Key is the register address. Value is the description.
FAN_INPUT_REGISTERS = {

    0x00: 'Firmware',
    0x01: 'Product code 1',
    0x02: 'Parameterset ID',
    0x03: 'Unique Device Signature 0',
    0x04: 'Unique Device Signature 1',
    0x05: 'Unique Device Signature 2',
    0x06: 'Unique Device Signature 3',
    0x07: 'Unique Device Signature 4',
    0x08: 'Unique Device Signature 5',
    0x09: 'Parameterset Index (from FW 13)',

    0x10: 'Operation condition 1',
    0x11: 'Operation condition 2',
    0x12: 'error status',
    0x13: 'error status 2 (from FW 14)',
    0x14: 'Speed',
    0x15: 'Motorcurrent',

    0x20: 'DC Voltage: V',
    0x21: 'Line voltage: V',
    0x22: 'IGBT-Temperature: C',
    0x23: 'inside Temperature: C',
    0x24: 'MCU Temperature: C',

    0x26: 'E1 Input',
    0x27: 'Modulation',

    0x30: 'Event',
    0x31: 'Event number',

    # Got no data for these two.
    # 0x33: 'Motor input power: W',

    # 0x49: 'Inquiry PIN protect level',

}


def _get(ser):
    """Get fan speed or get all registers we currently support."""
    if len(sys.argv) == 2:
        print 'Fan speed in rpm: {}'.format(_read_rpm(ser))
    elif sys.argv[2] == 'all':
        _read_all_fan(ser)
    elif sys.argv[2] == 'register':
        modbus_common.read_holding_register(ser, FAN_SLAVE_ADDRESS, int(sys.argv[3], 16))
    elif sys.argv[2] == 'input':
        modbus_common.read_input_register(ser, FAN_SLAVE_ADDRESS, int(sys.argv[3], 16))
    else:
        raise ValueError('Unexpected args')


def _read_all_fan(ser):
    """Get all registers from the fan."""
    # Not the fastest, but it works.
    logger.setLevel(logging.INFO)  # Or the output will be a mess.
    print '--- HOLDING REGISTERS ---'
    for register in sorted(FAN_HOLDING_REGISTERS.iterkeys()):
        data = modbus_common.read_holding_register(
            ser, FAN_SLAVE_ADDRESS, register)

        print '0x{:04x} 0x{:04x} {:06d} {}'.format(
            register,  # Register as hex short.
            data,  # Register data as hex.
            data,  # Register data as int.
            FAN_HOLDING_REGISTERS[register])  # Description.
        time.sleep(.1)

    print '--- INPUT REGISTERS ---'
    for register in sorted(FAN_INPUT_REGISTERS.iterkeys()):
        data = modbus_common.read_input_register(
            ser, FAN_SLAVE_ADDRESS, register)

        print '0x{:04x} 0x{:04x} {:06d} {}'.format(
            register,  # Register as hex short.
            data,  # Register data as hex.
            data,  # Register data as int.
            FAN_INPUT_REGISTERS[register])  # Description.
        time.sleep(.1)


def _read_rpm(ser):
    """
    Read the fan speed in rpm.
    :param ser: Serial connection to the fan controller.
    :return: The fan speed in rpm.
    """
    return modbus_common.get_fan_rpm_ecblue(ser, FAN_SLAVE_ADDRESS)


def _print_usage():
    """
    Basic usage tips.
    """
    print 'sudo -HE env PATH=$PATH ./ecbluefan.py {get|set|factory} [options]'
    print '\tget options:'
    print '\t\t <none>: speed in RPM.'
    print '\t\t all: registers.'
    print '\t\t register: get fan holding register in the form of 0x91c'
    print '\t\t input: get fan input register in the form of 0x91c'
    print '\tset options:'
    print '\t\t <integer> set speed in RPM. Setting speed under 10% of the max is not recommended.'
    print '\t\t register: set fan register in the form of 0x91c {data}'
    print '\tfactory: Restore factory defaults.'


def _set(ser):
    """Set fan speed to the RPM given in sys.argv[2]
    or write a hex value to a hex register.
    Example sudo ./ecbluefan.py set register 91c 1"""
    if sys.argv[2] == 'register':
        _write_fan_register(ser, int(sys.argv[3], 16), struct.pack('>H', int(sys.argv[4], 16)))
    else:
        speed_rpm = int(sys.argv[2])
        max_rpm = modbus_common.get_fan_max_rpm_ecblue(ser, FAN_SLAVE_ADDRESS)
        if speed_rpm < 0 or speed_rpm > max_rpm:
            raise ValueError("Speed setting {} must be between 0 (off) and {}.".format(
                speed_rpm, max_rpm))
        logger.debug('Setting fan speed to {} rpm.'.format(speed_rpm))
        write(ser, max_rpm, speed_rpm)


def write(ser, max_rpm, rpm_setting):
    """Set fan speed to the given RPM.
    :param ser: Serial connection to the fan controller.
    :param max_rpm: The maximum rpm of the fan motor.
    :param rpm_setting: The user supplied rpm setting.
    returns: The modbus write result."""
    return modbus_common.set_fan_rpm_ecblue(
        ser, FAN_SLAVE_ADDRESS, rpm_setting, max_rpm)


def _write_fan_register(ser, register, data):
    """
    Write arbitrary data to a fan controller register.
    :param ser: Serial connection to the fan controller.
    :param register: The register to write
    :param data: The data to write
    :return: The modbus write result.
    """
    client = dkmodbus.dkmodbus(ser)
    return client.write_multiple_registers(
        FAN_SLAVE_ADDRESS, register, 1, 2, data)


def main():
    """
    Main entry point.
    :return: Zero on success, nonzero on failure.
    """
    ser = serial.Serial("/dev/ttyUSB3", baudrate=19200, parity='E', timeout=0.15)
    if sys.argv[1] == 'get':
        _get(ser)
    elif sys.argv[1] == 'set':
        _set(ser)
    else:
        _print_usage()
        return 1
    return 0


if __name__ == '__main__':
    try:
        logger.debug('start: argv {}'.format(sys.argv))
        rc = main()
        logger.debug('end main {}'.format(rc))
        sys.exit(rc)
    except Exception as e:
        logger.exception(e)
        _print_usage()
        sys.exit(1)
