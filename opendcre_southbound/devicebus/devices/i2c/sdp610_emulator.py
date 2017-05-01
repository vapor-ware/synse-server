#!/usr/bin/env python
""" OpenDCRE Southbound I2C pressure sensor via emulator

    Author: Andrew Cencini
    Date:   10/21/2016

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

            # read back two bytes (CRC omitted for emulator)
            reading = serial_device.read(2)

            serial_device.flushInput()
            serial_device.flushOutput()

            # convert and return
            return reading

    except Exception, e:
        logger.exception(e)
        raise OpenDCREException('Caused by {} {}'.format(type(e), e.message)), None, sys.exc_info()[2]
