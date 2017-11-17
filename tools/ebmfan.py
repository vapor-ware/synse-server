#!/usr/bin/env python

""" Run this off the command line by:
sudo -HE env PATH=$PATH ./ebmfan.py get

Command line tool for the Ebm Papst fan controller.
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
from synse.protocols.modbus import modbus_common  # nopep8
from synse.protocols.conversions import conversions  # nopep8

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Set to DEBUG for detailed packet traces.

# Fan controller holding registers. Key is the register address. Value is the description.
FAN_HOLDING_REGISTERS = {
    0xD000: 'Reset',
    0xD001: 'Set Value',  # TODO: Looks like the speed setting.
    0xD002: 'Password',
    0xD003: 'Password',
    0xD004: 'Password',
    0xD005: 'Factory Setting Control',  # This will restore factory defaults or set what they defaults are.
    0xD006: 'Customer Setting Control',

    0xD009: 'Operating Hours Counter',
    0xD00A: 'Operating Minutes Counter',
    0xD00C: 'Addressing On/Off',  # Won't likely need.
    0xD00D: 'Stored Set Value (parameter set 1)',
    0xD00E: 'Stored Set Value (parameter set 2)',
    0xD00F: 'Enable / Disable',
    0xD010: 'Remote Control Output 0-10 V',

    0xD100: 'Fan Address',
    0xD101: 'Set Value Source',
    0xD102: 'Preferred Running Direction',
    0xD103: 'Store Set Value',
    0xD104: 'Switch for Parameter Set Source',
    0xD105: 'Parameter Set Internal',
    0xD106: 'Operating Mode (parameter set 1)',
    0xD107: 'Operating Mode (parameter set 2)',
    0xD108: 'Controller function (parameter set 1)',
    0xD109: 'Controller function (parameter set 2)',
    0xD10A: 'P factor (parameter set 1)',
    0xD10B: 'P factor (parameter set 2)',
    0xD10C: 'I factor (parameter set 1)',
    0xD10D: 'I factor (parameter set 2)',
    0xD10E: 'Max Modulation Level (parameter set 1)',
    0xD10F: 'Max Modulation Level (parameter set 2)',

    0xD110: 'Min Modulation Level (parameter set 1)',
    0xD111: 'Min Modulation Level (parameter set 2)',
    0xD112: 'Motor Stop Enable (parameter set 1)',
    0xD113: 'Motor Stop Enable (parameter set 2)',

    0xD116: 'Starting Modulation Level',
    0xD117: 'Max Permissible Modulation Level',  # TODO: Check this out.
    0xD118: 'Min Permissible Modulation Level',  # TODO: Check this out.
    0xD119: 'Maximum Speed',  # TODO: Check this out.
    0xD11A: 'Maximum Permissible Speed',  # TODO: Check this out.

    0xD11F: 'Ramp-Up Time',

    0xD120: 'Ramp-Down Time',

    0xD128: 'Speed Limit',  # TODO: Check this out.

    0xD12A: 'Input char. curve point 1 X-coordinate (par. 1)',
    0xD12B: 'Input char. curve point 1 Y-coordinate (par. 1)',
    0xD12C: 'Input char. curve point 2 X-coordinate (par. 1)',
    0xD12D: 'Input char. curve point 2 Y-coordinate (par. 1)',
    0xD12E: 'Source for Controller Function',  # TODO: Check this out.
    0xD12F: 'Limitation Control',

    0xD130: 'Function output 0..10 V / speed monitoring',

    0xD135: 'Maximum Permissible Power',
    0xD136: 'Max Power at derating end.',
    0xD137: 'Module temperature power derating start',
    0xD138: 'Module temperature power derating end',

    0xD13B: 'Maximum Winding Current',
    0xD13C: 'Input char. curve point 1 X-coordinate (par. 2)',
    0xD13D: 'Input char. curve point 1 Y-coordinate (par. 2)',
    0xD13E: 'Input char. curve point 2 X-coordinate (par. 2)',
    0xD13F: 'Input char. curve point 2 Y-coordinate (par. 2)',

    0xD140: 'Char. curve output 0..10 V point 1 X',
    0xD141: 'Char. curve output 0..10 V point 1 Y',
    0xD142: 'Char. curve output 0..10 V point 2 X',
    0xD143: 'Char. curve output 0..10 V point 2 Y',

    0xD145: 'Run Monitoring Speed Limit',

    0xD147: 'Sensor Acutal Value Source',
    0xD148: 'Switch for Rotating Direction Source',
    0xD149: 'Communication Speed',  # TODO: Baud Rate probably
    0xD14A: 'Parity Configuration',  # TODO: Need this

    0xD14D: 'Motor temperature power derating start',
    0xD14E: 'Motor temperature power derating end',

    0xD150: 'Shedding Function',
    0xD151: 'Max Start PWM Shedding',
    0xD152: 'Max Number of Start Attempts',
    0xD153: 'Relay Drop-out Delay',

    0xD155: 'Maximum Power',

    0xD158: 'Configuration I/O 1',
    0xD159: 'Configuration I/O 2',
    0xD15A: 'Configuration I/O 3',
    0xD15B: 'Rotating Direction Fail-Safe Mode',
    0xD15C: 'Fail-Safe Set Value Source',
    0xD15D: 'Set Value Fail-Safe Speed',
    0xD15E: 'Time Lag Fail-Safe Speed',
    0xD15F: 'Cable Break Detection Voltage',

    0xD160: 'Minimum Sensor Value',
    0xD161: 'Minimum Sensor Value',
    0xD162: 'Maximum Sensor Value',
    0xD163: 'Maximum Sensor Value',
    0xD164: 'Sensor Unit',
    0xD165: 'Sensor Unit',
    0xD166: 'Sensor Unit',
    0xD167: 'Sensor Unit',
    0xD168: 'Sensor Unit',
    0xD169: 'Sensor Unit',
    0xD16A: 'Switch for Enable / Disable Source',
    0xD16B: 'Stored Enable / Disable',
    0xD16C: 'Switch for Set Value Source',
    0xD16D: 'Power Derating Ramp',
    0xD16E: 'Voltage Output',
    0xD16F: 'RFID Access',

    0xD170: 'Customer Data',
    0xD171: 'Customer Data',
    0xD172: 'Customer Data',
    0xD173: 'Customer Data',
    0xD174: 'Customer Data',
    0xD175: 'Customer Data',
    0xD176: 'Customer Data',
    0xD177: 'Customer Data',
    0xD178: 'Customer Data',
    0xD179: 'Customer Data',
    0xD17A: 'Customer Data',
    0xD17B: 'Customer Data',
    0xD17C: 'Customer Data',
    0xD17D: 'Customer Data',
    0xD17E: 'Customer Data',
    0xD17F: 'Customer Data',

    0xD180: 'Operating Hours Counter (backup)',

    0xD182: 'Error Indicator',

    0xD184: 'First Error',
    0xD185: 'Time of First Error',
    0xD186: 'Error History / Time',
    0xD187: 'Error History / Time',
    0xD188: 'Error History / Time',
    0xD189: 'Error History / Time',
    0xD18A: 'Error History / Time',
    0xD18B: 'Error History / Time',
    0xD18C: 'Error History / Time',
    0xD18D: 'Error History / Time',
    0xD18E: 'Error History / Time',
    0xD18F: 'Error History / Time',

    0xD190: 'Error History / Time',
    0xD191: 'Error History / Time',
    0xD192: 'Error History / Time',
    0xD193: 'Error History / Time',
    0xD194: 'Error History / Time',
    0xD195: 'Error History / Time',
    0xD196: 'Error History / Time',
    0xD197: 'Error History / Time',
    0xD198: 'Error History / Time',
    0xD199: 'Error History / Time',
    0xD19A: 'Error History / Time',
    0xD19B: 'Error History / Time',
    0xD19C: 'Error History / Time',
    0xD19D: 'Error History / Time',
    0xD19E: 'Error History / Time',
    0xD19F: 'Error History / Time',

    0xD1A0: 'DC-Link Voltage Reference Value',
    0xD1A1: 'DC-Link Current Reference Value',
    0xD1A2: 'Fan Serial Number',
    0xD1A3: 'Fan Serial Number',
    0xD1A4: 'Date of Fan Manufacture',
    0xD1A5: 'Fan Type',
    0xD1A6: 'Fan Type',
    0xD1A7: 'Fan Type',
    0xD1A8: 'Fan Type',
    0xD1A9: 'Fan Type',
    0xD1AA: 'Fan Type',

    0xD1F7: 'Rotor position sensor calibration set value',
    0xD1F8: 'Rotor position sensor calibration',
}

# Fan controller input registers. Key is the register address. Value is the description.
FAN_INPUT_REGISTERS = {
    0xD000: 'Identification',
    0xD001: 'Maximum Number of Bytes',
    0xD002: 'Bus Controller Software Name',
    0xD003: 'Bus Controller Software Version',
    0xD004: 'Commutation Controller Software Name',
    0xD005: 'Commutation Controller Software Version',
    # 0xD006: '',
    # 0xD007: '',
    # 0xD008: '',
    # 0xD009: '',
    # 0xD00a: '',
    # 0xD00b: '',
    # 0xD00c: '',
    # 0xD00d: '',
    # 0xD00e: '',
    # 0xD00f: '',

    0xD010: 'Actual Speed',
    0xD011: 'Motor Status',
    0xD012: 'Warning',
    0xD013: 'DC-Link Voltage',
    0xD014: 'DC-Link Current',
    0xD015: 'Module Temperature',
    0xD016: 'Motor Temperature',
    0xD017: 'Electronics Temperature',
    0xD018: 'Current Direction of Rotation',
    0xD019: 'Current Modulation Level',
    0xD01a: 'Current Set Value',
    0xD01b: 'Sensor Actual Value',
    0xD01c: 'Enable / Disable Input State',
    0xD01d: 'Current Parameter Set',
    0xD01e: 'Current Controller Function',
    # 0xD01f: '',

    # 0xD020: '',
    0xD021: 'Current Power',
    # 0xD022: '',
    0xD023: 'Sensor Actual Value 1',
    0xD024: 'Sensor Actual Value 2',
    # 0xD025: '',
    # 0xD026: '',
    0xD027: 'Current Power W',
    0xD028: 'Current Set Value Source',
    0xD029: 'Energy Consumption Power',
    0xD02a: 'Energy Consumption Power',
    # 0xD02b: '',
    # 0xD02c: '',
    # 0xD02d: '',
    # 0xD02e: '',
    # 0xD02f: '',

}


def _get(ser):
    """Get fan speed or get all registers we currently support."""
    if len(sys.argv) == 2:
        print 'Fan speed in rpm: {}'.format(_read_rpm(ser))
    elif sys.argv[2] == 'all':
        _read_all_fan(ser)
    elif sys.argv[2] == 'register':
        modbus_common.read_fan_register(ser, int(sys.argv[3], 16))
    else:
        raise ValueError('Unexpected args')


def _read_all_fan(ser):
    """Get all registers from the fan."""
    # Not the fastest, but it works.
    logger.setLevel(logging.INFO)  # Or the output will be a mess.
    print '--- HOLDING REGISTERS ---'
    for register in sorted(FAN_HOLDING_REGISTERS.iterkeys()):
        client = dkmodbus.dkmodbus(ser)
        register_data = client.read_holding_registers(1, register, 1)

        print '0x{:04x} 0x{} {:06d} {}'.format(
            register,                                   # Register as hex short.
            hexlify(register_data),                     # Register data as hex.
            conversions.unpack_word(register_data),     # Register data as unsigned short.
            FAN_HOLDING_REGISTERS[register])            # Description.
        time.sleep(.1)

    print '--- INPUT REGISTERS ---'
    for register in sorted(FAN_INPUT_REGISTERS.iterkeys()):
        client = dkmodbus.dkmodbus(ser)
        register_data = client.read_input_registers(1, register, 1)

        print '0x{:04x} 0x{} {:06d} {}'.format(
            register,                                   # Register as hex short.
            hexlify(register_data),                     # Register data as hex.
            conversions.unpack_word(register_data),     # Register data as unsigned short.
            FAN_INPUT_REGISTERS[register])              # Description.
        time.sleep(.1)


def _read_rpm(ser):
    client = dkmodbus.dkmodbus(ser)
    result = client.read_holding_registers(1, 0x2107, 1)  # TODO: Need the correct register(s) here.
    return conversions.unpack_word(result)


def _print_usage():
    print 'sudo -HE env PATH=$PATH ./ebmfan.py {get|set} [options]'
    print '\tget options:'
    print '\t\t <none>: speed in RPM.'
    print '\t\t all: registers.'
    print '\t\t register: get fan register in the form of 0x91c'
    print '\tset options:'
    print '\t\t <integer> set speed in RPM. Setting a speed under 10% of the max is not recommended.'
    print '\t\t register: set fan register in the form of 0x91c {data}'
    # print '\ttemp: gets temperature and humidity'
    # print '\tambient: gets ambient temperature'
    # print '\tair: gets CEC airflow'
    # print '\tair_status: gets CEC airflow status register.'
    # print '\ttherm: gets all thermistors'
    # print '\tpressure: gets all differential pressures'
    # print '\tled [<state>[<color> <blink_state>]]: Read or write to the LED controller.'


def _set(ser):
    """Set fan speed to the RPM given in sys.argv[2]
    or write a hex value to a hex register.
    Example sudo ./gs3fan.py set register 91c 1"""
    if sys.argv[2] == 'register':
        _write_fan_register(ser, int(sys.argv[3], 16), struct.pack('>H', int(sys.argv[4], 16)))
    else:
        speed_rpm = int(sys.argv[2])
        max_rpm = modbus_common.get_fan_max_rpm_gs3(ser)
        if speed_rpm < 0 or speed_rpm > max_rpm:
            raise ValueError("Speed setting {} must be between 0 (off) and {}.".format(
                speed_rpm, max_rpm))
        logger.debug('Setting fan speed to {}'.format(speed_rpm))
        write(ser, max_rpm, speed_rpm)


# TODO: Get the correct register(s)
def write(ser, max_rpm, rpm_setting):
    """Set fan speed to the given RPM.
    :param ser: Serial connection to the gs3 fan controller.
    :param max_rpm: The maximum rpm of the fan motor.
    :param rpm_setting: The user supplied rpm setting.
    returns: The modbus write result."""

    client = dkmodbus.dkmodbus(ser)

    if rpm_setting == 0:    # Turn the fan off.
        result = client.write_multiple_registers(
            1,      # Slave address.
            0x91B,  # Register to write to.
            1,      # Number of registers to write to.
            2,      # Number of bytes to write.
            '\x00\x00')      # Data to write.

    else:           # Turn the fan on at the desired RPM.
        rpm_to_hz = modbus_common.get_fan_rpm_to_hz_gs3(ser, max_rpm)
        hz = rpm_setting * rpm_to_hz
        logger.debug('Set rpm to {}, Hz to {}'.format(rpm_setting, hz))
        packed_hz = conversions.fan_gs3_packed_hz(hz)

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
    # if sys.argv[1] == 'reset' and sys.argv[2] == 'usb':
    #     return _reset_usb()  # Do this without trying to open the serial port. We may not be able to open it.
    #
    # # i2c stuff is first to avoid the serial (don't need it).
    # if sys.argv[1] == 'therm':
    #     _read_thermistors()
    #     return 0
    # elif sys.argv[1] == 'pressure':
    #     _read_differential_pressures()
    #     return 0
    # elif sys.argv[1] == 'led':
    #     _led()
    #     return 0

    ser = serial.Serial("/dev/ttyUSB3", baudrate=19200, parity='E', timeout=0.15)
    if sys.argv[1] == 'get':
        _get(ser)
    elif sys.argv[1] == 'set':
        _set(ser)
    # elif sys.argv[1] == 'temp':
    #     _read_temperature_and_humidity(ser)
    # elif sys.argv[1] == 'air':
    #     _read_airflow(ser)
    # elif sys.argv[1] == 'air_status':
    #     return _read_airflow_status(ser)
    # elif sys.argv[1] == 'test1':
    #     _test1(ser)
    # elif sys.argv[1] == 'ambient':
    #     _read_temperature_ambient(ser)
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