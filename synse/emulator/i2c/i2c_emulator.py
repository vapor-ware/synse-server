#!/usr/bin/env python
""" An I2C emulator used for testing I2C capabilities of Synse.

When invoked, takes a single command line argument pointing to the
config file to be used by the emulator.

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

import json
import logging
import sys

import serial
import vapor_common.vapor_logging as vapor_logging

logger = logging.getLogger(__name__)

emulator_config = dict()


def _flush_all(serial_device):
    """ Flush input and output for a given device.

    Args:
        serial_device (serial.Serial): the device to flush.
    """
    serial_device.flushInput()
    serial_device.flushOutput()


def main():
    """ The main body of the emulator - listens for incoming requests and
    processes them.

    Starts by initializing the context from config, then listening on the
    given serial device.
    """
    serial_device_name = emulator_config['serial_device']
    devices = emulator_config['devices']
    counts = emulator_config['_counts']

    with serial.Serial(serial_device_name, baudrate=115200, timeout=None) as serial_device:
        _flush_all(serial_device)

        logger.error('! Flushed serial input and output.')

        while True:
            try:
                # read sequence: <cmd> <addr> <len> [<bytes>]
                cmd = serial_device.read(1)
                addr = str(ord(serial_device.read(1)))
                write_buf_len = ord(serial_device.read(1))
                logger.error('<< cmd {} addr {} write_buf_len {}'.format(cmd, addr, write_buf_len))

                if cmd == 'R':
                    # look up addr in devices and counts and return its data
                    # (len is ignored on 'R')
                    if addr in devices:
                        if isinstance(devices[addr], list) and len(devices[addr]) > 0 and \
                                isinstance(devices[addr][0], list):
                            counts[addr] = 0 if addr not in counts else counts[addr]
                            _count = counts[addr] if addr in counts else 0

                            serial_device.write([int(x, 16) for x in devices[addr][_count]])
                            logger.error('>> bytes: {}'.format([int(x, 16) for x in
                                                                devices[addr][_count]]))

                            _count += 1
                            counts[addr] = _count % len(devices[addr])
                        else:
                            serial_device.write([int(x, 16) for x in devices[addr]])
                            logger.error(
                                '>> bytes: {}'.format([int(x, 16) for x in devices[addr]]))
                    else:
                        logger.error('! Not found: {}'.format(addr))

                elif cmd == 'W':
                    # look up addr in devices, and write len bytes (which are to be read here)
                    # to the device entry
                    buf = serial_device.read(write_buf_len)
                    if addr in devices:
                        devices[addr] = [format(ord(x), 'x') for x in buf]
                        logger.error('<< bytes: {}'.format([format(ord(x), 'x') for x in buf]))

                        # the '1' means the write succeeded
                        serial_device.write(['1'])
                        logger.error('>> response: ["1"]')
                    else:
                        logger.error('! Not found: {}'.format(addr))

            except Exception, ex:
                # let's clean up now, shall we
                _flush_all(serial_device)
                logger.error('! Flushed serial input and output. ({})'.format(ex))

if __name__ == '__main__':

    vapor_logging.setup_logging(default_path='/synse/configs/logging/emulator.json')

    # the emulator config file is the one and only param passed to the emulator
    emulator_config_file = sys.argv[1]

    # parse and validate config
    # logger.info('Using emulator file {}'.format(emulator_config_file))
    logger.error('Using emulator file {}'.format(emulator_config_file))
    with open(emulator_config_file, 'r') as config_file:
        emulator_config = json.load(config_file)

    # stick a _counts dictionary to track cycling through responses for each device
    emulator_config['_counts'] = dict()

    logger.error('-----------------------------------------------------------------------')
    logger.error('Started I2C emulator on ({})'.format(emulator_config['serial_device']))
    logger.error('-----------------------------------------------------------------------')

    while True:
        try:
            main()
        except Exception as e:
            logger.exception('Exception encountered. (%s)', e)
