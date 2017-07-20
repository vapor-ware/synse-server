#!/usr/bin/env python
""" Utilities for background sensor reads.

Author: Erick Daniszewski
Date:   19 July 2017

\\//
 \/apor IO
"""

import errno
import datetime
import os
from binascii import hexlify
from functools import wraps

import constants


def crc8(data):
    """ CRC checker for the data out of the SDP600 (differential
    pressure sensor).

    Args:
        data (str): data read from the SDP600 sensor.

    Returns:
        bool: True if CRC check passed; False otherwise.
    """
    crc = 0
    for char in data:
        crc ^= ord(char)
        for _ in range(8):
            if crc & 0x80:
                crc = (crc << 1) ^ constants.POLYNOMIAL1
            else:
                crc <<= 1

    return crc == ord(data[2])


def crc_check(data):
    """ Modbus CRC check.

    Args:
        data (str): data read from modbus.

    Returns:
        bool: True if CRC check passed; False otherwise.
    """
    crc = 0xFFFF

    # do not include the 2 byte crc in crc calculation
    for char in data[:-2]:
        crc ^= ord(char)
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) & constants.POLYNOMIAL2
            else:
                crc >>= 1

    # construct the received crc (last two bytes). the CEC sends it
    # backwards
    rx_crc = int(hexlify(data[-1:-3:-1]), 16)

    return crc == rx_crc


def crc_calc(data):
    """ Calculate the CRC for modbus.

    Args:
        data (str): data read from modbus.

    Returns:
        int: the calculated CRC value.
    """
    crc = 0xFFFF

    for char in data:
        crc ^= ord(char)
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ constants.POLYNOMIAL2
            else:
                crc >>= 1

    return crc


def timestamped(f):
    """ Decorator to add a timestamp to the return of the decorated method.

    Args:
        f: function to be decorated.
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        ts = datetime.datetime.utcnow()
        return ts, f(*args, **kwargs)
    return wrapper


def mkdir_p(path):
    """ mkdir -p like functionality. this will create the specified
    directory if it doesn't exist.

    Args:
        path (str): the path to create, if it does not already exist.
    """
    try:
        os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise
