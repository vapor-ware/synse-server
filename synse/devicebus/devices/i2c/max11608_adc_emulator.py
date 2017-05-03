#!/usr/bin/env python
""" Synse I2C thermistor via MAX11608 ADC

    Author: Andrew Cencini
    Date:   10/18/2016

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
import logging
from synse.errors import SynseException

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

            # read back two bytes
            reading = serial_device.read(2)
            logger.info('<< Reading: {}'.format([hex(ord(i)) for i in reading]))
            reading = (ord(reading[0]) << 8) + ord(reading[1])

            serial_device.flushInput()
            serial_device.flushOutput()

            # convert and return
            return reading

    except Exception, e:
        logger.exception(e)
        raise SynseException('Caused by {} {}'.format(type(e), e.message)), None, sys.exc_info()[2]
