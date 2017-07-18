#!/usr/bin/env python

""" Run this off the command line by:
sudo -HE env PATH=$PATH ./gs3fan.py get
"""

import sys
import os
import serial
import logging
from binascii import hexlify
import struct
import time

# before we import the synse protocol packages, we want to make sure it
# is reachable on the pythonpath
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from synse.protocols.modbus import dkmodbus  # nopep8
from synse.protocols.conversions import conversions  # nopep8
from synse.protocols.i2c_common import i2c_common  # nopep8

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed packet traces.

# Fan controller registers. Key is the register address. Value is the description.
FAN_CONTROLLER_REGISTERS = {

    # P0.X Motor Parameters
    0x0000: 'Motor Nameplate Voltage',
    0x0001: 'Motor Nameplate Amps',
    0x0002: 'Motor Base Frequency',
    0x0003: 'Motor Base RPM',
    0x0004: 'Motor Maximum RPM',
    0x0005: 'Motor Auto Tune',
    0x0006: 'Motor Line to Line Resistance R1',
    0x0007: 'Motor No-Load Current',

    # P1.X Ramp Parameters
    0x0100: 'Stop Methods',
    0x0101: 'Acceleration Time 1',
    0x0102: 'Deceleration Time 1',
    0x0103: 'Accel S-curve',
    0x0104: 'Decel S-curve',
    0x0105: 'Acceleration Time 2',
    0x0106: 'Deceleration Time 2',
    0x0107: 'Select method to use - 2nd Accel/Decel',
    0x0108: 'Accel 1 to Accel 2 frequency transition',
    0x0109: 'Decel 2 to Decel 1 frequency transition',
    0x010a: 'Skip Frequency 1',
    0x010b: 'Skip Frequency 2',
    0x010c: 'Skip Frequency 3',
    0x010d: 'Skip Frequency 4',
    0x010e: 'Skip Frequency 5',
    # gap
    0x0111: 'Skip Frequency Band',
    0x0112: 'DC Injection Current Level',
    # gap
    0x0114: 'DC Injection during Start-up',
    0x0115: 'DC Injection during Stopping',
    0x0116: 'Start-point for DC Injection',

    # P2.X Volts/ Hertz Parameters
    0x0200: 'Volts/Hertz Settings',
    0x0201: 'Slip Compensation',
    0x0202: 'Auto-torque Boost',
    0x0203: 'Torque Compensation Time Constant',
    0x0204: 'Mid-point Frequency',
    0x0205: 'Mid-point Voltage',
    0x0206: 'Min. Output Frequency',
    0x0207: 'Min. Output Voltage',
    0x0208: 'PWM Carrier Frequency',
    0x0209: 'Slip Compensation Time Constant',
    0x020a: 'Control Mode',

    # P3.X Digital Parameters
    0x0300: 'Source of Operation Command',
    0x0301: 'Multi-Function Input Terminals (DI1 - DI2)',
    0x0302: 'Multi-Function Input Terminal 3 (DI3)',
    0x0303: 'Multi-Function Input Terminal 4 (DI4)',
    0x0304: 'Multi-Function Input Terminal 5 (DI5)',
    0x0305: 'Multi-Function Input Terminal 6 (DI6)',
    0x0306: 'Multi-Function Input Terminal 7 (DI7)',
    0x0307: 'Multi-Function Input Terminal 8 (DI8)',
    0x0308: 'Multi-Function Input Terminal 9 (DI9)',
    0x0309: 'Multi-Function Input Terminal 10 (DI10)',
    0x030a: 'Multi-Function Input Terminal 11 (DI11)',
    0x030b: 'Multi-Function Output Terminal 1 (Relay Output)',
    0x030c: 'Multi-Function Output Terminal 2 (DO1)',
    0x030d: 'Multi-Function Output Terminal 3 (DO2)',
    0x030e: 'Multi-Function Output Terminal 4 (DO3)',
    # gap
    0x0310: 'Desired Frequency',
    0x0311: 'Desired Current',
    0x0312: 'PID Deviation Level',
    0x0313: 'PID Deviation Time',
    0x0314: 'Desired Frequency 2',
    # gap
    0x031e: 'Frequency Output (FO) Scaling Factor',
    0x031f: '2nd Source of Operation Command',

    # P4.X Analog Parameters
    0x0400: 'Source of Frequency Command',
    0x0401: 'Analog Input Offset Polarity',
    0x0402: 'Analog Input Offset',
    0x0403: 'Analog Input Gain',
    0x0404: 'Analog Input Reverse Motion Enable',
    0x0405: 'Loss of AI2 Signal (4-20 mA)',
    # gap
    0x040b: 'Analog Output Signal',
    0x040c: 'Analog Output Gain',
    0x040d: '2nd Source of Frequency Command',
    0x040e: '2nd Frequency Command Offset Polarity',
    0x040f: '2nd Frequency Command Offset',
    0x0410: '2nd Frequency Command Gain',
    0x0411: 'Trim Frequency Reference',
    0x0412: 'Trim Mode Select',

    # P5.X Presets Parameters
    0x0500: 'Jog',
    0x0501: 'Multi-Speed 1',
    0x0502: 'Multi-Speed 2',
    0x0503: 'Multi-Speed 3',
    0x0504: 'Multi-Speed 4',
    0x0505: 'Multi-Speed 5',
    0x0506: 'Multi-Speed 6',
    0x0507: 'Multi-Speed 7',
    0x0508: 'Multi-Speed 8',
    0x0509: 'Multi-Speed 9',
    0x050a: 'Multi-Speed 10',
    0x050b: 'Multi-Speed 11',
    0x050c: 'Multi-Speed 12',
    0x050d: 'Multi-Speed 13',
    0x050e: 'Multi-Speed 14',
    0x050f: 'Multi-Speed 15',

    # P6.X Protection Parameters
    0x0600: 'Electronic Thermal Overload Relay',
    0x0601: 'Auto Restart after Fault',
    0x0602: 'Momentary Power Loss',
    0x0603: 'Reverse Operation Inhibit',
    0x0604: 'Auto Voltage Regulation',
    0x0605: 'Over-Voltage Stall Protection',
    0x0606: 'Auto Adjustable Accel/Decel',
    0x0607: 'Over-Torque Detection Mode',
    0x0608: 'Over-Torque Detection Level',
    0x0609: 'Over-Torque Detection Time',
    0x060a: 'Over-Current Stall Prevention during Acceleration',
    0x060b: 'Over-Current Stall Prevention during Operation',
    0x060c: 'Maximum Allowable Power Loss Time',
    0x060d: 'Base-Block Time for Speed Search',
    0x060e: 'Maximum Speed Search Current Level',
    0x060f: 'Upper Bound of Output Frequency',
    0x0610: 'Lower Bound of Output Frequency',
    0x0611: 'Over-Voltage Stall Prevention Level',
    0x0612: 'Braking Voltage Level',
    # gap
    0x061e: 'Line Start Lockout',
    0x061f: 'Present Fault Record',
    0x0620: 'Second Most Recent Fault Record',
    0x0621: 'Third Most Recent Fault Record',
    0x0622: 'Fourth Most Recent Fault Record',
    0x0623: 'Fifth Most Recent Fault Record',
    0x0624: 'Sixth Most Recent Fault Record',
    0x0625: 'Hunting Gain',

    # P7.X PID Parameters
    0x0700: 'Input Terminal for PID Feedback',
    0x0701: 'PV 100% Value',
    0x0702: 'PID Setpoint Source',
    0x0703: 'PID Feedback Gain',
    0x0704: 'PID Setpoint Offset Polarity',
    0x0705: 'PID Setpoint Offset',
    0x0706: 'PID Setpoint Gain',
    # gap
    0x070a: 'Keypad & Serial PID Setpoint',
    0x070b: 'PID Multi-setpoint 1',
    0x070c: 'PID Multi-setpoint 2',
    0x070d: 'PID Multi-setpoint 3',
    0x070e: 'PID Multi-setpoint 4',
    0x070f: 'PID Multi-setpoint 5',
    0x0710: 'PID Multi-setpoint 6',
    0x0711: 'PID Multi-setpoint 7',
    # gap
    0x0714: 'Proportional Control',
    0x0715: 'Integral Control',
    0x0716: 'Derivative Control',
    0x0717: 'Upper Bound for Integral Control',
    0x0718: 'Derivative Filter Time Constant',
    0x0719: 'PID Output Frequency Limit',
    0x071a: 'Feedback Signal Detection Time',
    0x071b: 'PID Feedback Loss',
    0x071c: 'PID Feedback Loss Preset Speed',

    # P8.X Display Parameters
    0x0800: 'User Defined Display Function',
    0x0801: 'Frequency Scale Factor',
    0x0802: 'Backlight Timer',

    # P9.X Communications Parameters
    0x0900: 'Communication Address',
    0x0901: 'Transmission Speed',
    0x0902: 'Communication Protocol',
    0x0903: 'Transmission Fault Treatment',
    0x0904: 'Time Out Detection',
    0x0905: 'Time Out Duration',
    # gap
    0x0907: 'Parameter Lock',
    # NOT TOUCHING THIS FOR FEAR OF MESSING UP MODBUS REMOTELY. 0x0908: 'Restore to Default',
    # gap
    0x090b: 'Block Transfer Parameter 1',
    0x090c: 'Block Transfer Parameter 2',
    0x090d: 'Block Transfer Parameter 3',
    0x090e: 'Block Transfer Parameter 4',
    0x090f: 'Block Transfer Parameter 5',
    0x0910: 'Block Transfer Parameter 6',
    0x0911: 'Block Transfer Parameter 7',
    0x0912: 'Block Transfer Parameter 8',
    0x0913: 'Block Transfer Parameter 9',
    0x0914: 'Block Transfer Parameter 10',
    0x0915: 'Block Transfer Parameter 11',
    0x0916: 'Block Transfer Parameter 12',
    0x0917: 'Block Transfer Parameter 13',
    0x0918: 'Block Transfer Parameter 14',
    0x0919: 'Block Transfer Parameter 15',
    0x091a: 'Serial Comm (RS-485) Speed Reference',
    0x091b: 'Serial Comm RUN Command',
    0x091c: 'Serial Comm Direction Command',
    0x091d: 'Serial Comm External Fault',
    0x091e: 'Serial Comm Fault Reset',
    0x091f: 'Serial Comm JOG Command',
    # gap
    0x0927: 'Firmware Version',
    0x0928: 'Parameter Copy',
    0x0929: 'GS Series Number',
    0x092a: 'Manufacturer Model Information',

    # P10.X Encoder Feedback Parameters
    0x0a00: 'Encoder Pulse per Revolution',
    0x0a01: 'Encoder type Input',
    0x0a02: 'Proportional Control',
    0x0a03: 'Integral Control',
    0x0a04: 'Speed Control Output Speed Limit',
    0x0a05: 'Encoder Loss Detection',

    # Status Addresses
    0x2100: 'StatusMonitor 1',
    0x2101: 'StatusMonitor 2',
    0x2102: 'Frequency Command F (XXX.X)',
    0x2103: 'Output Frequency H (XXX.X)',
    0x2104: 'Output Current A',
    0x2105: 'DC Bus Voltage d (XXX.X)',
    0x2106: 'Output Voltage U (XXX.X)',
    0x2107: 'Motor RPM',
    0x2108: 'Scale Frequency (Low Word)',
    0x2109: 'Scale Frequency (High Word)',
    0x210a: 'Power Factor Angle',
    0x210b: '% Load (Output Current / Drive Rated Current) x 100',
    0x210c: 'PID Setpoint',
    0x210d: 'PID Feedback Signal (PV)',
    # gap
    0x2110: 'Firmware Version',
}


def _get(ser):
    """Get fan speed or get all registers we currently support."""
    if len(sys.argv) == 2:
        print 'Fan speed in rpm: {}'.format(_read_rpm(ser))
    elif sys.argv[2] == 'all':
        _read_all_fan(ser)
    elif sys.argv[2] == 'register':
        _read_fan_register(ser, int(sys.argv[3], 16))
    else:
        raise ValueError('Unexpected args')


def _print_usage():
    print 'sudo -HE env PATH=$PATH ./gs3fan.py {get|set|temp|ambient|air|therm|pressure} [options]'
    print '\tget options:'
    print '\t\t <none>: speed in RPM.'
    print '\t\t all: registers.'
    print '\t\t register: get fan register in the form of 0x91c'
    print '\tset options:'
    print '\t\t <integer> set speed in RPM (0 < 1755). settings from 1 to 174 are not recommended.'
    print '\t\t register: set fan register in the form of 0x91c {data}'
    print '\ttemp: gets temperature and humidity'
    print '\tambient: gets ambient temperature'
    print '\tair: gets CEC airflow'
    print '\ttherm: gets all thermistors'
    print '\tpressure: gets all differential pressures'


def _read_airflow(ser):
    client = dkmodbus.dkmodbus(ser)
    result = client.read_input_registers(2, 8, 1)
    logger.debug('result {}'.format(hexlify(result)))
    velocity = conversions.airflow_f660(result)
    print 'Airflow velocity = {} mm/s.'.format(velocity)
    velocity_cfm = conversions.flow_mm_s_to_cfm(velocity)
    print 'Airflow velocity = {} CFM'.format(velocity_cfm)


def _read_all_fan(ser):
    """Get all registers from the fan."""
    # Not the fastest, but it works.
    logger.setLevel(logging.INFO)  # Or the output will be a mess.
    for register in sorted(FAN_CONTROLLER_REGISTERS.iterkeys()):
        client = dkmodbus.dkmodbus(ser)
        register_data = client.read_holding_registers(1, register, 1)

        print '0x{:04x} 0x{} {:06d} {}'.format(
            register,                                   # Register as hex short.
            hexlify(register_data),                     # Register data as hex.
            conversions.unpack_word(register_data),     # Register data as unsigned short.
            FAN_CONTROLLER_REGISTERS[register])         # Description.
        time.sleep(.1)


def _read_differential_pressures():
    # Configure for 9 bit resolution.
    if i2c_common.configure_differential_pressure(1) != 0:
        print 'Failed to configure 9 bit resolution for differential pressure sensor on channel 1.'
        return 1
    if i2c_common.configure_differential_pressure(2) != 0:
        print 'Failed to configure 9 bit resolution for differential pressure sensor on channel 2.'
        return 1
    if i2c_common.configure_differential_pressure(4) != 0:
        print 'Failed to configure 9 bit resolution for differential pressure sensor on channel 4.'
        return 1
    readings = i2c_common.read_differential_pressures(3)
    # TODO: Should try to read 4 sensors when only 3 ports exist on current hardware.
    counter = 0
    for reading in readings:
        print 'Differential Pressure [{}]: {} Pa'.format(counter, reading)
        counter += 1


def _read_fan_register(ser, register):
    client = dkmodbus.dkmodbus(ser)
    register_data = client.read_holding_registers(1, register, 1)
    result = conversions.unpack_word(register_data)
    print '0x{}'.format(result)
    return result


def _read_rpm(ser):
    client = dkmodbus.dkmodbus(ser)
    result = client.read_holding_registers(1, 0x2107, 1)
    return conversions.unpack_word(result)


def _read_temperature_ambient(ser):
    # Slave address is 3. Register is 0 for temp, 1 for humidity.

    client = dkmodbus.dkmodbus(ser)
    result = client.read_input_registers(3, 0, 2)

    logger.debug('result {}'.format(hexlify(result)))
    temperature_raw = int(hexlify(result[0:2]), 16)
    humidity_raw = int(hexlify(result[2:4]), 16)
    logger.debug('temperature_raw {}'.format(temperature_raw))
    logger.debug('humidity_raw {}'.format(humidity_raw))
    temperature = conversions.temperature_sht31(result)
    humidity = conversions.humidity_sht31(result)
    print "Temperature = %0.2f C" % temperature
    print "Relative Humidity = %0.2f %%" % humidity


def _read_temperature_and_humidity(ser):
    # Slave address is 2. Register is 0 for temp, 1 for humidity.

    client = dkmodbus.dkmodbus(ser)
    result = client.read_input_registers(2, 0, 2)

    logger.debug('result {}'.format(hexlify(result)))
    temperature_raw = int(hexlify(result[0:2]), 16)
    humidity_raw = int(hexlify(result[2:4]), 16)
    logger.debug('temperature_raw {}'.format(temperature_raw))
    logger.debug('humidity_raw {}'.format(humidity_raw))
    temperature = conversions.temperature_sht31(result)
    humidity = conversions.humidity_sht31(result)
    print "Temperature = %0.2f C" % temperature
    print "Relative Humidity = %0.2f %%" % humidity


def _read_thermistors():
    """Read all thermistors from the CEC board. A reading of -1 indicates that
    no thermistor is present."""
    # TODO: Should try to read 12 thermistors when only 8 ports exist on current hardware.
    readings = i2c_common.read_thermistors(8)
    counter = 0
    for reading in readings:
        print 'Thermistor [{}]: {} C'.format(counter, reading)
        counter += 1


def _reset_usb():
    """Reset the usb in the event it disappeared due to the FTDI driver bug."""
    dkmodbus.dkmodbus.reset_usb([1, 2])
    return 0


def _set(ser):
    """Set fan speed to the RPM given in sys.argv[2]
    or write a hex value to a hex register.
    Example sudo ./gs3fan.py set register 91c 1"""
    if sys.argv[2] == 'register':
        _write_fan_register(ser, int(sys.argv[3], 16), struct.pack('>H', int(sys.argv[4], 16)))
    else:
        speed_rpm = int(sys.argv[2])
        if speed_rpm < 0 or speed_rpm > 1755:
            raise ValueError("Speed setting {} must be between 0 (off) and 1755.".format(speed_rpm))
        logger.debug('Setting fan speed to {}'.format(speed_rpm))
        write(ser, speed_rpm)


def _test1(ser):
    """Set fan speed to zero, then read relevant status registers.
    Output results in a human readable way.
    Increment to top speed, then back down.
    This test may not seem like much, but we had problems getting a response
    from the CEC board at high fan speeds. There is likely noise coming from
    the fan. We are using better shielding in production than we used for the
    prototype.
    It's a good test to ensure that retry is working.
    """
    logger.setLevel(logging.INFO)  # Or the output will be a mess.
    speed_settings = [0, 100, 200, 300, 400, 500, 600, 700, 800, 900, 1000,
                      1100, 1200, 1300, 1400, 1500, 1600, 1700, 1755, 1700,
                      1600, 1500, 1400, 1300, 1200, 1100, 1000, 900, 800, 700,
                      600, 500, 400, 300, 200, 100, 0]
    registers = [0x2100, 0x2101, 0x2102, 0x2103, 0x2104, 0x2105, 0x2106, 0x2107,
                 0x2108, 0x2109, 0x210a, 0x210b, 0x210c, 0x210d]
    for speed_setting in speed_settings:
        print 'Setting fan speed to {} rpm'.format(speed_setting)
        write(ser, speed_setting)
        time.sleep(10)  # May take a bit to slow down (it coasts AFAIK).
        print 'Fan speed in rpm: {}'.format(_read_rpm(ser))

        # Read out the status registers that seem useful.
        print 'Register HexData Decimal  Description'
        for register in registers:
            client = dkmodbus.dkmodbus(ser)
            register_data = client.read_holding_registers(1, register, 1)
            print '0x{:04x}   0x{}  {:06d}   {}'.format(
                register,  # Register as hex short.
                hexlify(register_data),  # Register data as hex.
                conversions.unpack_word(register_data),  # Register data as unsigned short.
                FAN_CONTROLLER_REGISTERS[register])      # Description.

            time.sleep(.1)


def write(ser, rpm):
    """Set fan speed to the given RPM."""
    client = dkmodbus.dkmodbus(ser)

    if rpm == 0:    # Turn the fan off.
        result = client.write_multiple_registers(
            1,      # Slave address.
            0x91B,  # Register to write to.
            1,      # Number of registers to write to.
            2,      # Number of bytes to write.
            '\x00\x00')      # Data to write.

    else:           # Turn the fan on at the desired RPM.
        packed_hz = conversions.fan_gs3_2010_rpm_to_packed_hz(rpm)
        result = client.write_multiple_registers(
            1,      # Slave address.
            0x91A,  # Register to write to.
            2,      # Number of registers to write to.
            4,      # Number of bytes to write.
            packed_hz + '\x00\x01')  # Frequency setting in Hz / data # 01 is on, # 00 is off.

    return result


def _write_fan_register(ser, register, data):
    client = dkmodbus.dkmodbus(ser)
    client.write_multiple_registers(1, register, 1, 2, data)


def main():
    if sys.argv[1] == 'reset' and sys.argv[2] == 'usb':
        return _reset_usb()  # Do this without trying to open the serial port. We may not be able to open it.

    # i2c stuff is first to avoid the serial (don't need it).
    if sys.argv[1] == 'therm':
        _read_thermistors()
        return 0
    elif sys.argv[1] == 'pressure':
        _read_differential_pressures()
        return 0

    ser = serial.Serial("/dev/ttyUSB3", baudrate=19200, parity='E', timeout=0.15)
    if sys.argv[1] == 'get':
        _get(ser)
    elif sys.argv[1] == 'set':
        _set(ser)
    elif sys.argv[1] == 'temp':
        _read_temperature_and_humidity(ser)
    elif sys.argv[1] == 'air':
        _read_airflow(ser)
    elif sys.argv[1] == 'test1':
        _test1(ser)
    elif sys.argv[1] == 'ambient':
        _read_temperature_ambient(ser)
    else:
        _print_usage()
        return 1
    return 0


if __name__ == '__main__':
    try:
        logger.debug('start: argv {}'.format(sys.argv))
        main()
        logger.debug('end main')
    except Exception as e:
        logger.exception(e)
        _print_usage()
