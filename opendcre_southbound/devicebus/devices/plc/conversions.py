#!/usr/bin/env python
""" Conversion functions for supported devices requiring a conversion from raw value.

    Author: Andrew Cencini
    Date:   09/21/2016
    
    \\//
     \/apor IO

-------------------------------
Copyright (C) 2015-17  Vapor IO

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
from opendcre_southbound.errors import BusDataException


def convert_thermistor(adc):
    """ Calculate a real world value from temperature device raw data.

    Args:
        adc (int): the value from the device to be converted.

    Returns:
        float: the thermistor temperature value, in Celsius
    """
    if adc >= 0xFFFF:
        raise BusDataException('Thermistor reading value > 0xFFFF received.')
    else:
        if adc > 745:
            temperature = (adc * -0.131) + 118.638
        elif adc > 542:
            temperature = (adc * -0.0985) + 93.399
        elif adc > 354:
            temperature = (adc * -0.106) + 97.66
        elif adc > 218:
            temperature = (adc * -0.147) + 112.046
        else:
            temperature = (adc * -0.235) + 131.294
        return float('%.2f' % round(temperature, 2))


def convert_humidity(raw):
    """ Convert a raw sensor value into humidity and temperature values.

    Args:
        raw (int): the raw sensor reading.

    Returns:
        tuple[float, float]: a 2-tuple of humidity, temperature values
            converted from raw value.
    """
    # True humidity is calculated by the following formula:
    # Real World Humidity = humidity/((2^14)-2) * 100
    if raw > 0xFFFFFFFF:
        raise BusDataException('Humidity reading value > 0xFFFFFFFF received.')
    else:
        humidity = raw >> 16
        humidity &= 0x3fff
        humidity = humidity / ((1 << 14) - 2.0) * 100

        # True temperature is calculated by the following formula:
        # Real World Temp (C) = temperature/((2^14)-2) * 165 - 40
        temperature = raw & 0x0000FFFF
        temperature = (((temperature >> 2) / 16382.0) * 165.0) - 40.0

        # temperature = temperature/((1<<14)-2.0) * 165 - 40
        return float('%.2f' % round(humidity, 2)), float('%.2f' % round(temperature, 2))


def convert_direct_pmbus(raw, reading_type, r_sense=1.0):
    """ Converts a raw voltage / current PMBUS value to a human-readable/real
    value.

    Args:
        raw (int): the raw PMBUS direct value
        reading_type (str): the type of reading being converted. Supported
            values include: 'current', 'voltage', and 'power'
        r_sense (int): the milliohm value for the sense resistor, used to
            compute m coefficient. if r_sense causes m to be > 32767, then
            we must divide m by 10, and increase the R coefficient by 1
            (per p30 of ADM1276 data sheet)

    Returns:
        float: a converted decimal value corresponding to the raw reading.
    """
    if reading_type == 'current':
        m = 807.0 * r_sense
        b = 20745.0
        r = -1.0
    elif reading_type == 'voltage':
        # we are operating in the 0-20V range here
        m = 19199.0
        b = 0.0
        r = -2.0
    elif reading_type == 'power':
        m = 6043.0 * r_sense
        b = 0.0
        r = -2.0
    else:
        raise BusDataException('Invalid reading_type specified for PMBUS direct conversion: {}'.format(reading_type))

    return (1.0 / m) * (raw * 10.0 ** (-r) - b)
