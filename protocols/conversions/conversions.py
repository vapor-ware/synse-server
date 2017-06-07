#!/usr/bin/env python
"""
        \\//
         \/apor IO


        Common file for sensor conversions. We need conversions in at least
        three places.
        1. Synse emulators.
        2. Synse physical hardware.
        3. Synse command line tools.

        This file is a common place for them.
        In order to share the code, this should not be under synse-server/synse
        because the __init__.py brings in many dependencies.
"""

import logging
import struct
from binascii import hexlify

logger = logging.getLogger(__name__)


def airflow_d6f_w10a1(reading):
    """Return the airflow velocity in millimeters per second given the raw two
    byte reading from the d6f w10a1 airflow sensor.
    :param reading: The raw two byte reading from the d6f w10a1 airflow sensor.
    :returns: The airflow velocity in millimeters per second."""
    return unpack_word(reading)


def fan_gs3_2010_rpm_to_packed_hz(rpm):
    """Convert an rpm setting for the gs3 2010 fan controller to Hz and packs
    the result into bytes. Setting the fan to a given rpm requires it.
    Does no input range validation.
    :param rpm: User provided rpm setting.
    :returns: Hz packed into two bytes."""
    hz = float(rpm) / 29.22
    logger.debug('Set rpm to {}, Hz to {}'.format(rpm, hz))
    shifted_hz = int(hz * 10)
    logger.debug('shifted_hz: {}'.format(shifted_hz))
    packed_hz = struct.pack('>H', shifted_hz)
    logger.debug('packed_hz {}'.format(hexlify(packed_hz)))
    return packed_hz


def flow_mm_s_to_cfm(mm_s):
    """Convert flow from mm/s to cubic feet per minute.
    This works for airflow on the V1 chamber based on the cross section of the
    chimney and the size of the fan. It may or may not work in the future.
    Dimensions could change.
    :param mm_s: Flow velocity in millimeters per second.
    :returns: The volume flow in cfm."""
    return mm_s * 6.28


def humidity_sht31(reading):
    """Convert the raw humidity reading from the sht31 humidity sensor to
    percent.
    :param reading: The reading from the sht31 humidity sensor.
    :returns: The humidity reading in percent."""
    return (unpack_word(reading[2:4]) / 65535.0) * 100


def humidity_sht31_int(reading):
    """Convert the raw humidity reading from the sht31 humidity sensor to
    percent.
    :param reading: The reading from the sht31 humidity sensor as an int.
    :returns: The humidity reading in percent."""
    return (reading / 65535.0) * 100


def temperature_sht31(reading):
    """Convert the raw temperature reading from the sht31 humidity sensor to
    degrees Celsius.
    :param reading: The first byte of the reading from the sht31 humidity
    sensor.
    :returns: The temperature reading in degrees Celsius."""
    return ((unpack_word(reading[0:2]) / 65535.0) * 175) - 45


def temperature_sht31_int(reading):
    """Convert the raw temperature reading from the sht31 humidity sensor to
    degrees Celsius.
    :param reading: The reading from the sht31 humidity sensor as an int.
    :returns: The temperature reading in degrees Celsius."""
    return ((reading / 65535.0) * 175) - 45


def unpack_byte(reading):
    """Unpack a single byte sensor reading given the byte.
    :param reading: The raw single byte sensor reading."""
    return struct.unpack('>B', reading)[0]


def unpack_word(reading):
    """Unpack a two byte word sensor reading given the bytes.
    :param reading: The raw two byte word sensor reading."""
    return struct.unpack('>H', reading)[0]
