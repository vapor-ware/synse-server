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
    """
    """

    path = '/synse/dev/{}'.format(device_name)

    utils.mkdir_p(path)

    with open(os.path.join(path, device_address), 'w') as f:
        f.write(
            '{}\t{}'.format(timestamp, data)
        )


def write_sdp610(timestamp, readings):
    """ Write the SDP-610 readings to file.

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
    """ Write the MAX-11608 readings to file.

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
