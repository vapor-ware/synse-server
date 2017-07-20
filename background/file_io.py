#!/usr/bin/env python
""" Helpers to handle the file writes for sensor reads.

    Author: Erick Daniszewski
    Date:   19 July 2017

    \\//
     \/apor IO
"""

import os

import constants
import utils


def write(device_name, device_address, timestamp, data):
    """ Helper method to write sensor data to file.
    """

    path = '/synse/dev/{}'.format(device_name)

    utils.mkdir_p(path)

    with open(os.path.join(path, str(device_address)), 'w') as f:
        f.write(
            '{}\t{}'.format(timestamp, data)
        )


def write_sdp610(timestamp, readings):
    """ Write the SDP-610 (differential pressure) readings to file.

    Data will be written tab separated in the form:
    TIMESTAMP   PRESSURE

    Args:
        timestamp (str): the timestamp the readings were taken at.
        readings (dict[int:int]): a mapping of sensor channel to sensor reading.
    """
    for addr, data in readings.iteritems():
        write(
            device_name=constants.SDP_610,
            device_address=addr,
            timestamp=timestamp,
            data=data
        )


def write_max11608(timestamp, readings):
    """ Write the MAX-11608 (thermistor) readings to file.

    Data will be written tab separated in the form:
    TIMESTAMP   TEMPERATURE

    Args:
        timestamp (str): the timestamp the readings were taken at.
        readings (dict[int:int]): a mapping of sensor channel to sensor reading.
    """
    for addr, data in readings.iteritems():
        write(
            device_name=constants.MAX_11608,
            device_address=addr,
            timestamp=timestamp,
            data=data
        )


def write_sht31(timestamp, readings):
    """ Write the SHT31 (humidity) readings to file.

    Data will be written tab separated in the form:
    TIMESTAMP   TEMPERATURE    HUMIDITY

    Args:
        timestamp (str): the timestamp the readings were taken at.
        readings (list): a list containing the readings where idx 0 contains
            the temperature reading, and idx 1 contains the humidity reading.
    """
    data = '{}\t{}'.format(*readings)

    write(
        device_name=constants.SHT31,
        device_address=0,  # fixme - tbd what this value should be
        timestamp=timestamp,
        data=data
    )


def write_f660(timestamp, readings):
    """ Write the F660 (airflow) readings to file.

    Data will be written tab separated in the form:
    TIMESTAMP   VELOCITY    TEMPERATURE

    Args:
        timestamp (str): the timestamp the readings were taken at.
        readings (list): a list containing the readings where idx 0 contains
            the velocity reading, and idx 1 contains the temperature reading.
    """
    data = '{}\t{}'.format(*readings)

    write(
        device_name=constants.F660,
        device_address=0,  # fixme - tbd what this value should be
        timestamp=timestamp,
        data=data
    )
