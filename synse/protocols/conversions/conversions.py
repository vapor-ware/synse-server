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
"""

import logging
import struct
from binascii import hexlify

logger = logging.getLogger(__name__)


def airflow_f660(reading):
    """Return the airflow velocity in millimeters per second given the raw two
    byte reading from the F660 airflow sensor.
    :param reading: The raw two byte reading from the F660 airflow sensor.
    :returns: The airflow velocity in millimeters per second."""
    return unpack_word(reading)


def convert_thermistor_reading(ad_reading, index, device_name):
    """Convert the thermistor reading for the given device_name.
    :param ad_reading: The raw reading from the thermistor from the A/D
    converter.
    :param index: The index into the raw reading to convert. This is underneath
    a bulk read. Two bytes per individual thermistor reading in ad_reading.
    :param device_name: The type of A/D converter that the thermistor is
    plugged in to. max-11610 and max-1108 are supported.
    :returns: The temperature in degrees C, or None if no thermistor attached.
    :raises: ValueError on unsupported device_name."""
    if device_name == 'max-11610':
        temperature = thermistor_max11610_adc(
            ad_reading[index:index + 2])
    elif device_name == 'max-11608':
        temperature = thermistor_max11608_adc(
            ad_reading[index:index + 2])
    else:
        raise ValueError('Unsupported device type {}.'.format(device_name))
    return temperature


def differential_pressure_sdp610(reading, altitude):
    """Return the differential pressure reading in Pascals given the raw three
    byte reading from the sdp610 differential pressure sensor.
    :param reading: The raw three byte reading from the sdp610 differential
    pressure sensor.
    :param altitude: (int | float): the altitude in meters above sea level.
    :returns: The differential pressure reading in Pascals."""
    # Third byte off the raw reading is the crc. Ignore that.
    data = unpack_word(reading[:2])

    if data & 0x8000:
        data = (~data + 1) & 0xFFFF
        data = -data
    correction = differential_pressure_sdp610_altitude(altitude)
    return data * correction


def differential_pressure_sdp610_altitude(altitude):
    """This needs to be separated from differential_pressure_sdp610 for now
    since some tests directly call it.
    Get the altitude correction factor, given an altitude in meters.

    http://www.mouser.com/ds/2/682/Sensirion_Differential_Pressure_SDP6x0series_Datas-767275.pdf

    Args:
        altitude (int | float): the altitude in meters above sea level.

    Returns:
        float: The conversion factor."""
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


def fan_gs3_packed_hz(hz):
    """Pack the hertz setting for writing the fan speed into the format that
    the gs3 fan controller wants.
    :param hz: The fan speed setting in hz.
    :returns: hz shifted and packed into two bytes.
    """
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


def _calculate_linear_fit_temperature(raw, slope, x1, y1):
    """
    Calculate the linear fit temperature given the raw reading, slope, x and y
    on the graph.
    :param raw: The raw temperature reading from the A/D converter. (int)
    :param slope: The linear approximation slope. (int array)
    :param x1: x range for the slope approximation. (int array)
    :param y1: y for the slope approximation. (int array)
    :return: The temperature reading. (int)
    """
    # Convert to 10 bit decimal.
    raw &= 0x3FF

    # Calculate the Linear Fit temperature
    if raw >= x1[0]:
        # Region 7
        temperature = slope[0] * (raw - x1[0]) + y1[0]
    elif x1[1] <= raw <= x1[0] - 1:
        # Region 6
        temperature = slope[1] * (raw - x1[1]) + y1[1]
    elif x1[2] <= raw <= x1[1] - 1:
        # Region 5
        temperature = slope[2] * (raw - x1[2]) + y1[2]
    elif x1[3] <= raw <= x1[2] - 1:
        # Region 4
        temperature = slope[3] * (raw - x1[3]) + y1[3]
    elif x1[4] <= raw <= x1[3] - 1:
        # Region 3
        temperature = slope[4] * (raw - x1[4]) + y1[4]
    elif x1[5] <= raw <= x1[4] - 1:
        # Region 2
        temperature = slope[5] * (raw - x1[5]) + y1[5]
    elif x1[6] <= raw <= x1[5] - 1:
        # Region 1
        temperature = slope[6] * (raw - x1[6]) + y1[6]
    else:
        # Hit max temperature of the thermistor
        temperature = 105.0

    return temperature


def thermistor_max11608_adc(reading):
    """Convert the raw two byte reading from the max11608-adc thermistor to
    degrees Celsius.
    :param reading: The two byte reading from the max11608-adc thermistor.
    :returns: The temperature reading in degrees Celsius or None if no thermistor
    is present."""
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

    return _calculate_linear_fit_temperature(raw, slope, x1, y1)


def thermistor_max11608_adc_49(reading):
    """Convert the raw two byte reading from the max11608-adc thermistor to
    degrees Celsius. Use this function for 4.9 volts.
    :param reading: The two byte reading from the max11608-adc thermistor.
    :returns: The temperature reading in degrees Celsius or None if no thermistor
    is present."""
    raw = unpack_word(reading)
    if raw == 0xFFFF:
        # All f means no thermistor plugged in.
        return None

    # These are used for converting raw thermistor readings to Celsius.
    # From spreadsheet Sun Thermistor Plot MAX11608.xlxs with V of 4.9V
    slope = [-0.072, -0.07677, -0.10646, -0.15385, -0.24242, -0.37143, -0.5]
    x1 = [644, 390, 253, 165, 113, 76, 55]
    y1 = [18, 38, 53, 67, 80, 94, 105]

    return _calculate_linear_fit_temperature(raw, slope, x1, y1)


def thermistor_max11610_adc(reading):
    """Convert the raw two byte reading from the max11610-adc thermistor to
    degrees Celsius.
    :param reading: The two byte reading from the max11610-adc thermistor.
    :returns: The temperature reading in degrees Celsius or None if no thermistor
    is present."""
    raw = unpack_word(reading)
    if raw == 0xFFFF:
        # All f means no thermistor plugged in.
        return None

    # These are used for converting raw thermistor readings to Celsius.
    # Values used for slope intercept equation for temperature linear fit
    # temperature = slope(ADC_VALUE - X1) + Y1
    # From spreadsheet Sun Thermistor Plot MAX11610.xlxs and V of 4.8V
    slope = [-0.07347, -0.07835, -0.10895, -0.15663, -0.25263, -0.37143, -0.52632]
    x1 = [631, 382, 248, 161, 111, 74, 54]
    y1 = [18, 38, 53, 67, 80, 94, 105]

    return _calculate_linear_fit_temperature(raw, slope, x1, y1)


def unpack_byte(reading):
    """Unpack a single byte sensor reading given the byte.
    :param reading: The raw single byte sensor reading."""
    return struct.unpack('>B', reading)[0]


def unpack_word(reading):
    """Unpack a two byte word sensor reading given the bytes.
    :param reading: The raw two byte word sensor reading."""
    return struct.unpack('>H', reading)[0]
