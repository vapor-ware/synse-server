#!/usr/bin/env python
""" Common sensor conversions.

These are needed in at least three places:
 1. Synse emulators.
 2. Synse physical hardware.
 3. Synse command line tools.

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
import struct
from binascii import hexlify

logger = logging.getLogger(__name__)


def airflow_f660(reading):
    """ Return the airflow velocity in millimeters per second given the raw two
    byte reading from the F660 airflow sensor.

    Args:
        reading: The raw two byte reading from the F660 airflow sensor.

    Returns:
        The airflow velocity in millimeters per second.
    """
    return unpack_word(reading)


def differential_pressure_sdp610(reading, altitude):
    """ Return the differential pressure reading in Pascals given the raw three
    byte reading from the sdp610 differential pressure sensor.

    Args:
        reading: The raw three byte reading from the sdp610 differential
            pressure sensor.
        altitude (int | float): the altitude in meters above sea level.

    Returns:
        The differential pressure reading in Pascals.
    """
    # Third byte off the raw reading is the crc. Ignore that.
    data = unpack_word(reading[:2])

    if data & 0x8000:
        data = (~data + 1) & 0xFFFF
        data = -data
    correction = differential_pressure_sdp610_altitude(altitude)
    return data * correction


def differential_pressure_sdp610_altitude(altitude):
    """ This needs to be separated from differential_pressure_sdp610 for now
    since some tests directly call it.

    Get the altitude correction factor, given an altitude in meters.
    http://www.mouser.com/ds/2/682/Sensirion_Differential_Pressure_SDP6x0series_Datas-767275.pdf

    Args:
        altitude (int | float): the altitude in meters above sea level.

    Returns:
        float: The conversion factor.
    """
    # Altitude below zero is not specified in the datasheet. Use the lowest specified.
    if altitude < 250:
        corr = 0.95
    elif altitude < 425:
        corr = 0.98
    elif altitude < 500:
        corr = 1.00
    elif altitude < 750:
        corr = 1.01
    elif altitude < 1500:
        corr = 1.04
    elif altitude < 2250:
        corr = 1.15
    elif altitude < 3000:
        corr = 1.26
    else:
        corr = 1.38

    return corr


def fan_gs3_2010_rpm_to_packed_hz(rpm):
    """ Convert an rpm setting for the gs3 2010 fan controller to Hz and packs
    the result into bytes. Setting the fan to a given rpm requires it.

    Does no input range validation.

    Args:
        rpm: User provided rpm setting.

    Returns:
        Hz packed into two bytes.
    """
    # User manual for the gs3 fan controller is here:
    # https://cdn.automationdirect.com/static/manuals/gs3m/gs3m.pdf

    # We use the result of this function to set register
    # P9.26 / Serial Comm Speed Reference.

    # This conversion is not in the manual, but can be derived from the
    # register range of 0.0 to 400.0 Hz and the rpm range of 0 to 1755.
    hz = float(rpm) / 29.22
    logger.debug('Set rpm to {}, Hz to {}'.format(rpm, hz))

    # We shift the hz value here since the register is set by BCD (binary coded
    # decimal) except in tenths of Hz. Typically floats are not used on control
    # systems, so this is a 16 bit int (word). In order to get tenths of Hz,
    # we multiply by 10 which is a BCD shift.
    shifted_hz = int(hz * 10)
    logger.debug('shifted_hz: {}'.format(shifted_hz))
    packed_hz = struct.pack('>H', shifted_hz)
    logger.debug('packed_hz {}'.format(hexlify(packed_hz)))
    return packed_hz


def flow_mm_s_to_cfm(mm_s):
    """ Convert flow from mm/s to cubic feet per minute.
    This works for airflow on the V1 chamber based on the cross section of the
    chimney and the size of the fan. It may or may not work in the future.
    Dimensions could change.

    Args:
        mm_s: Flow velocity in millimeters per second.

    Returns:
        The volume flow in cfm.
    """
    return mm_s * 6.28


def humidity_sht31(reading):
    """ Convert the raw humidity reading from the sht31 humidity sensor to
    percent.

    Args:
        reading: The reading from the sht31 humidity sensor.

    Returns:
        The humidity reading in percent.
    """
    return (unpack_word(reading[2:4]) / 65535.0) * 100


def humidity_sht31_int(reading):
    """ Convert the raw humidity reading from the sht31 humidity sensor to
    percent.

    Args:
        reading: The reading from the sht31 humidity sensor as an int.

    Returns:
        The humidity reading in percent.
    """
    return (reading / 65535.0) * 100


def temperature_sht31(reading):
    """ Convert the raw temperature reading from the sht31 humidity sensor to
    degrees Celsius.

    Args:
        reading: The first byte of the reading from the sht31 humidity
            sensor.

    Returns:
        The temperature reading in degrees Celsius.
    """
    return ((unpack_word(reading[0:2]) / 65535.0) * 175) - 45


def temperature_sht31_int(reading):
    """ Convert the raw temperature reading from the sht31 humidity sensor to
    degrees Celsius.

    Args:
        reading: The reading from the sht31 humidity sensor as an int.

    Returns:
        The temperature reading in degrees Celsius.
    """
    return ((reading / 65535.0) * 175) - 45


def thermistor_max11608_adc(reading):
    """ Convert the raw two byte reading from the max11608-adc thermistor to
    degrees Celsius.

    Args:
        reading: The two byte reading from the max11608-adc thermistor.

    Returns:
        The temperature reading in degrees Celsius or None if no thermistor
        is present.
    """
    raw = unpack_word(reading)
    if raw == 0xFFFF:
        # All f means no thermistor plugged in.
        return None

    # These are used for converting raw thermistor readings to Celsius.
    # Values used for slope intercept equation for temperature linear fit
    # temperature = slope(ADC_VALUE - X1) + Y1
    # From spreadsheet Brian Elect Thermistor Plot MAX11608.xlxs
    slope = [-0.07031, -0.076, -0.10448, -0.15476, -0.23077, -0.35135, -0.55556]
    x1 = [656, 399, 259, 171, 116, 77, 58]
    y1 = [18, 38, 53, 67, 80, 94, 105]

    # Convert to 10 bit decimal.
    raw &= 0x3FF

    # Calculate the Linear Fit temperature
    if raw >= 656:
        # Region 7
        temperature = slope[0] * (raw - x1[0]) + y1[0]
    elif 399 <= raw <= 655:
        # Region 6
        temperature = slope[1] * (raw - x1[1]) + y1[1]
    elif 250 <= raw <= 398:
        # Region 5
        temperature = slope[2] * (raw - x1[2]) + y1[2]
    elif 171 <= raw <= 258:
        # Region 4
        temperature = slope[3] * (raw - x1[3]) + y1[3]
    elif 116 <= raw <= 170:
        # Region 3
        temperature = slope[4] * (raw - x1[4]) + y1[4]
    elif 77 <= raw <= 115:
        # Region 2
        temperature = slope[5] * (raw - x1[5]) + y1[5]
    elif 58 <= raw <= 76:
        # Region 1
        temperature = slope[6] * (raw - x1[6]) + y1[6]
    else:
        # Hit max temperature of the thermistor
        temperature = 105.0

    return temperature


def unpack_byte(reading):
    """ Unpack a single byte sensor reading given the byte.

    Args:
        reading: The raw single byte sensor reading.
    """
    return struct.unpack('>B', reading)[0]


def unpack_word(reading):
    """ Unpack a two byte word sensor reading given the bytes.

    Args:
        reading: The raw two byte word sensor reading.
    """
    return struct.unpack('>H', reading)[0]
