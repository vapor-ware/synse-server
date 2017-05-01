#!/usr/bin/env python
""" OpenDCRE Southbound I2C LED control via emulator

    Author: Andrew Cencini
    Date:   10/25/2016

    \\//
     \/apor IO
"""
import logging
from opendcre_southbound.errors import OpenDCREException

import serial
import sys

logger = logging.getLogger(__name__)


def read_emulator(device_name, channel):
    # -- EMULATOR --
    try:
        # use self.device_name for serial device, 115200, 0.25
        with serial.Serial(device_name, baudrate=115200, timeout=0.5) as serial_device:
            serial_device.flushInput()
            serial_device.flushOutput()

            # write ['R', self.channel] to read this device
            serial_device.write([ord('R'), channel, 0x00])

            # read back 4 bytes - 0..2 are color, 3 is ledstate
            reading = serial_device.read(4)

            serial_device.flushInput()
            serial_device.flushOutput()

            led_values = dict()
            led_values['color'] = (ord(reading[0]) << 16) | (ord(reading[1]) << 8) | ord(reading[2])

            if ord(reading[3]) == 0x00:
                led_values['state'] = 'off'
                led_values['blink'] = 'steady'
            elif ord(reading[3]) == 0x2a:
                led_values['state'] = 'on'
                led_values['blink'] = 'steady'
            elif ord(reading[3]) == 0x3f:
                led_values['state'] = 'on'
                led_values['blink'] = 'blink'
            else:
                raise OpenDCREException("Invalid LED State returned from emulator: {}".format(ord(reading[3])))

            return led_values

    except Exception, e:
        logger.exception(e)
        raise OpenDCREException('Caused by {} {}'.format(type(e), e.message)), None, sys.exc_info()[2]


def write_emulator(device_name, channel, color, ledstate, blinkstate):
    try:
        # use self.device_name for serial device, 115200, 0.25
        with serial.Serial(device_name, baudrate=115200, timeout=0.25) as serial_device:
            serial_device.flushInput()
            serial_device.flushOutput()

            if ledstate == 'off':
                ledstate = 0x00
            elif blinkstate == 'steady' and ledstate == 'on':
                ledstate = 0x2a
            elif blinkstate == 'blink' and ledstate == 'on':
                ledstate = 0x3f

            # write ['W', self.channel] to read this device
            serial_device.write([ord('W'), channel, 0x04])
            led_bytes = [color >> 16, (color >> 8) & 0xff, color & 0xff, ledstate]
            serial_device.write(led_bytes)

            # read back result byte
            reading = serial_device.read(1)
            if reading != '1':
                raise OpenDCREException('Invalid response received from emulator: {}'.format(reading))

            serial_device.flushInput()
            serial_device.flushOutput()

            # convert and return
            return reading
    except Exception, e:
        logger.exception(e)
        raise OpenDCREException('Caused by {} {}'.format(type(e), e.message)), None, sys.exc_info()[2]
