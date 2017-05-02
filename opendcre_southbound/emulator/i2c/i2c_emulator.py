#!/usr/bin/env python
""" An RS485 emulator for use in testing RS485 capabilities of OpenDCRE.

    When invoked, takes a single command line argument pointing to the config file to be used by the emulator.

    Author: Andrew Cencini
    Date:   10/11/2016

    \\//
     \/apor IO
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

    :param serial_device: The device to flush.
    :return: None.
    """
    serial_device.flushInput()
    serial_device.flushOutput()


def main():
    """ The main body of the emulator - listens for incoming requests and processes them.

    Starts by initializing the context from config, then listening on the given serial device.

    :return: None.
    """
    serial_device_name = emulator_config['serial_device']
    devices = emulator_config['devices']
    counts = emulator_config['_counts']

    with serial.Serial(serial_device_name, baudrate=115200, timeout=None) as serial_device:
        _flush_all(serial_device)

        logger.error("! Flushed serial input and output.")

        while True:
            try:
                # read sequence: <cmd> <addr> <len> [<bytes>]
                cmd = serial_device.read(1)
                addr = str(ord(serial_device.read(1)))
                write_buf_len = ord(serial_device.read(1))
                logger.error("<< cmd {} addr {} write_buf_len {}".format(cmd, addr, write_buf_len))

                if cmd == 'R':
                    # look up addr in devices and counts and return its data (len is ignored on 'R')
                    if addr in devices:
                        if isinstance(devices[addr], list) and len(devices[addr]) > 0 and isinstance(devices[addr][0], list):
                            counts[addr] = 0 if addr not in counts else counts[addr]
                            _count = counts[addr] if addr in counts else 0

                            serial_device.write([int(x, 16) for x in devices[addr][_count]])
                            logger.error(">> bytes: {}".format([int(x, 16) for x in devices[addr][_count]]))

                            _count += 1
                            counts[addr] = _count % len(devices[addr])
                        else:
                            serial_device.write([int(x, 16) for x in devices[addr]])
                            logger.error(">> bytes: {}".format([int(x, 16) for x in devices[addr]]))
                    else:
                        logger.error("! Not found: {}".format(addr))

                elif cmd == 'W':
                    # look up addr in devices, and write len bytes (which are to be read here) to the device entry
                    buf = serial_device.read(write_buf_len)
                    if addr in devices:
                        devices[addr] = [format(ord(x), 'x') for x in buf]
                        logger.error("<< bytes: {}".format([format(ord(x), 'x') for x in buf]))

                        # the '1' means the write succeeded
                        serial_device.write(['1'])
                        logger.error(">> response: ['1']")
                    else:
                        logger.error("! Not found: {}".format(addr))

            except Exception, ex:
                # let's clean up now, shall we
                _flush_all(serial_device)
                logger.error("! Flushed serial input and output. ({})".format(ex))

if __name__ == '__main__':

    vapor_logging.setup_logging(default_path='logging_emulator.json')

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
            logger.exception("Exception encountered. (%s)", e)
