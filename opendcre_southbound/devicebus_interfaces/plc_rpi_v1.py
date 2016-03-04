#!/usr/bin/env python
"""
   OpenDCRE Power Line Communication Configuration
   Author:  andrew
   Date:    12/9/2015

        \\//
         \/apor IO

Copyright (C) 2015-16  Vapor IO

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
import RPi.GPIO as GPIO
import time
import datetime
import serial

# Used to retry/abort wake operation if INH does not go high in this amount of time
WAKE_TIMEOUT_SECONDS = 1

# Bit rate for configuring SIG60 modem
DEFAULT_CONFIGURATION_BPS = 19200

# PIN ASSIGNMENTS (RPi.BOARD mode)
PLC_CMD_PIN = 13
PLC_FREQ_PIN = 19
PLC_HDI_PIN = 8
PLC_HDO_PIN = 10
PLC_INH_PIN = 15
PLC_SLEEP_PIN = 11
PLC_SELECT_PIN = 21     # switch comms to pic from PLC

# Available bit rates for low (<10Mhz) and high (>10Mhz) frequency comms
BIT_RATES_LO = (38400, 57600, 9600, 19200)
BIT_RATES_HI = (38400, 57600, 115200, 19200)

# Available frequency pairs
FREQUENCY_PAIRS = (
    (1.75, 4.5), (1.75, 5.5), (1.75, 6.0), (1.75, 6.5),
    (4.5, 5.5), (4.5, 6.0), (4.5, 6.5), (4.5, 10.5),
    (10.5, 13.0),
    (5.5, 10.5), (5.5, 13.0),
    (6.0, 10.5), (6.0, 13.0),
    (6.5, 10.5), (6.5, 13.0),
    (5.5, 6.5))

# Default configuration for non-serial-console setup
OPENDCRE_DEFAULT_CONFIGURATION = {
    'frequency_number': 1,
    'remote_loopback': False,
    'interference_hopping': False,
    'long_wum': True,
    'auto_sleep': True,
    'auto_wum': False,
    'loopback_enabled': False,
    'interference_detected': False,
    'f0': 5.5,
    'f1': 10.5,
    'bit_rate': 115200
}


def get_configuration(serial_device=None, frequency=0):
    """ Get the values stored in control registers 0 and 1.

    Keyword Args:
    :param serial_device: The name of the serial reader/writer device to use in getting configuration.
    :param frequency: The frequency to operate at (0 or 1) when getting configuration.

    Returns: A dictionary containing the values stored in control registers
        0 and 1.

    """
    if serial_device is None:
        raise ValueError("Must provide a valid serial reader/writer device name.")

    serial_device = serial.Serial(serial_device, baudrate=DEFAULT_CONFIGURATION_BPS)

    serial_device.flushInput()
    serial_device.flushOutput()

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    # Frequency Select
    GPIO.setup(PLC_FREQ_PIN, GPIO.OUT)
    if frequency == 0:
        GPIO.output(PLC_FREQ_PIN, False)
    else:
        GPIO.output(PLC_FREQ_PIN, True)

    # Sleep
    GPIO.setup(PLC_SLEEP_PIN, GPIO.IN)

    # Command
    GPIO.setup(PLC_CMD_PIN, GPIO.IN)

    # Select
    GPIO.setup(PLC_SELECT_PIN, GPIO.IN)

    # retrieve both control registers
    # pull cmd line low
    GPIO.setup(PLC_CMD_PIN, GPIO.OUT)
    GPIO.output(PLC_CMD_PIN, False)

    time.sleep(.001)

    # get control reg 0
    serial_device.write(chr(0x0D))
    reg0 = serial_device.read(size=1)

    # get control reg 1
    serial_device.write(chr(0x1D))
    reg1 = serial_device.read(size=1)

    # bring CMD back high
    GPIO.output(PLC_CMD_PIN, True)

    GPIO.cleanup()
    serial_device.close()
    # return friendly dict of config bytes
    return get_config_dict(reg0, reg1)


def get_config_dict(reg0=None, reg1=None):
    """ Convert two configuration register values to a more usable dictionary format.

    :param reg0: Configuration register 0 value (0x00..0xFF)
    :param reg1: Configuration register 1 value (0x00..0x0FF)
    :return: The configuration reflected in reg0 and reg1 as a dictionary, mapping
            bitfields to configuration params.
    """
    reg0 = ord(reg0)
    reg1 = ord(reg1)
    config = dict()

    # register 0
    config['frequency_number'] = reg0 & 0x01
    config['remote_loopback'] = bool((reg0 >> 1) & 0x01)
    config['interference_hopping'] = bool((reg0 >> 2) & 0x01)
    config['long_wum'] = bool((reg0 >> 3) & 0x01)
    config['auto_sleep'] = not((reg0 >> 4) & 0x01)
    config['auto_wum'] = not((reg0 >> 5) & 0x01)
    config['loopback_enabled'] = not((reg0 >> 6) & 0x01)
    config['interference_detected'] = bool((reg0 >> 7) & 0x01)

    # register 1
    freq_select = reg1 & 0x0F
    bit_rate = (reg1 >> 4) & 0x03

    (config['f0'], config['f1']) = FREQUENCY_PAIRS[freq_select]
    if config['frequency_number'] == 0:
        config['bit_rate'] = get_bitrate(bit_rate, config['f0'])
    else:
        config['bit_rate'] = get_bitrate(bit_rate, config['f1'])
    return config


def get_bitrate(bit_rate=0, freq=0):
    """ Get the bit rate for a given bit_rate/frequency pair.

    :param bit_rate: The raw bit rate value (0..3) from configuration register 1.
    :param freq: The frequency value (0..1) from configuration register 0.
    :return: The bit rate value for the given pair.
    """
    if 0 < freq < 10:
        return BIT_RATES_LO[bit_rate]
    else:
        return BIT_RATES_HI[bit_rate]


def configure(serial_device=None, configuration=None):
    """ Configure the PLC modem (serial connection must be re-configured to
    appropriate baud rate separately).

    Keyword Args:
    :param serial_device: The name of the serial reader/writer device to use in setting configuration.

    :param configuration: the configuration settings to apply to the modem.

    :return: None

    """
    if serial_device is not None and configuration is not None:
        serial_device = serial.Serial(serial_device, baudrate=DEFAULT_CONFIGURATION_BPS)
        serial_device.flushInput()
        serial_device.flushOutput()

        reg0 = configuration['frequency_number']
        reg0 |= int(configuration['remote_loopback']) << 1
        reg0 |= int(configuration['interference_hopping']) << 2
        reg0 |= int(configuration['long_wum']) << 3
        reg0 |= int(not(configuration['auto_sleep'])) << 4
        reg0 |= int(not(configuration['auto_wum'])) << 5
        reg0 |= int(not(configuration['loopback_enabled'])) << 6
        reg0 |= int(configuration['interference_detected']) << 7

        # TODO handle valueerror when key not found in tuple
        reg1 = FREQUENCY_PAIRS.index((configuration['f0'], configuration['f1']))
        if configuration['frequency_number'] == 0:
            if configuration['f0'] < 10:
                reg1 |= (BIT_RATES_LO.index(configuration['bit_rate']) << 4)
            else:
                reg1 |= (BIT_RATES_HI.index(configuration['bit_rate']) << 4)
        else:
            if configuration['f1'] < 10:
                reg1 |= (BIT_RATES_LO.index(configuration['bit_rate']) << 4)
            else:
                reg1 |= (BIT_RATES_HI.index(configuration['bit_rate']) << 4)

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)

        # Frequency Select
        GPIO.setup(PLC_FREQ_PIN, GPIO.OUT)
        if configuration['frequency_number'] == 0:
            GPIO.output(PLC_FREQ_PIN, False)
        else:
            GPIO.output(PLC_FREQ_PIN, True)

        # Sleep
        GPIO.setup(PLC_SLEEP_PIN, GPIO.IN)

        # Command
        GPIO.setup(PLC_CMD_PIN, GPIO.IN)

        # Select
        GPIO.setup(PLC_SELECT_PIN, GPIO.IN)

        # pull cmd line low
        GPIO.setup(PLC_CMD_PIN, GPIO.OUT)
        GPIO.output(PLC_CMD_PIN, False)

        time.sleep(.001)

        # write byte 1
        serial_device.write(chr(0x05))   # write to reg 0
        serial_device.write(chr(reg0))

        # write byte 2
        serial_device.write(chr(0x15))   # write to reg 1
        serial_device.write(chr(reg1))

        serial_device.flush()

        time.sleep(.001)

        # bring CMD back high
        GPIO.output(PLC_CMD_PIN, GPIO.IN)
        GPIO.cleanup()
        serial_device.close()


def wake():
    """ Wake up the PLC modem and all devices on the bus, on the frequency
    currently in use.

    First, check if the devices are awake; if so, do nothing, otherwise, trigger
    the nSleep line, wait 150ms (until HDO goes high), then return.  As such:

    WARNING: THIS FUNCTION CAN REQUIRE >150ms TO COMPLETE - USE WITH CARE!

    Returns: Nothing.

    Raises: WakeException if operation fails - may be retried if needed.
    :rtype: None

    """
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PLC_INH_PIN, GPIO.IN)            # INH (read)
    if not GPIO.input(PLC_INH_PIN):             # if asleep
        GPIO.setup(PLC_SLEEP_PIN, GPIO.OUT)     # nSleep (write)
        GPIO.output(PLC_SLEEP_PIN, GPIO.LOW)    # set Sleep low
        time.sleep(1.0/1000.0)                  # sleep 1ms
        GPIO.output(PLC_SLEEP_PIN, GPIO.HIGH)   # set nSleep high
        time.sleep(1.0/1000.0)                  # sleep 1ms
        start = datetime.datetime.now()
        while not GPIO.input(PLC_INH_PIN):      # wait for INH to go high
            end = datetime.datetime.now()
            if (end-start).seconds > WAKE_TIMEOUT_SECONDS:
                raise WakeException("PLC_INH_PIN did not go high before timeout.")
            time.sleep(1.0/1000.0)              # sleep 1ms
        time.sleep(150.0/1000.0)                # wait for WUM to be sent/HDO to go high
    GPIO.cleanup()
    # at this point, the SIG60 is awake and refreshed!


class WakeException(Exception):
    """ Exception raised when a wake command times out or fails.  May be
    used to trigger a retry.
    """
    pass
