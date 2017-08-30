#!/usr/bin/env python
"""
    \\//
     \/apor IO

     Common code for the sensor daemons.
"""

import errno
import os


def mkdir(path):
    """This is like mkdir -p.
    :param path: The directory to create."""
    # Can you say vapor_common? We may be able to resurrect that repo now.
    try:
        os.makedirs(path)
    except OSError as ex:
        if not (ex.errno == errno.EEXIST and os.path.isdir(path)):
            raise


def write_reading(path, reading):
    """Write a single sensor reading to a file at path.
    :param path: The file path to write the readings to.
    :param reading: The sensor reading to write."""
    write_readings(path, [reading])


def write_readings(path, readings):
    """Write sensor readings to a file at path. Each reading will be written in
    order, each on a single line.
    :param path: The file path to write the readings to.
    :param readings: The sensor readings to write line by line."""
    output = []
    for reading in readings:
        if reading is None:
            output.append('null' + os.linesep)
        else:
            output.append(str(reading) + os.linesep)

    # TODO: Lock around the write.
    with open(path, 'w') as f:
        f.writelines(output)
