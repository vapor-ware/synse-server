#!/usr/bin/env python
"""
    \\//
     \/apor IO

     Common code for the sensor daemons.
"""

import errno
import fcntl
import logging
import os
import time


logger = logging.getLogger(__name__)


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

    tries = 3  # Up to 3 tries.
    for attempt in range(tries):
        try:
            with open(path, 'w') as f:
                try:  # Write under exclusive file lock.
                    fcntl.flock(f, fcntl.LOCK_EX)
                    f.writelines(output)
                    break  # Success.
                finally:
                    fcntl.flock(f, fcntl.LOCK_UN)

        except Exception:
            next_attempt = attempt + 1
            if next_attempt < tries:
                logger.exception(
                    'Failed writing sensor file {}. Will retry.'.format(path))
                time.sleep(.05)  # Wait 50 ms for the lock to be released.
            else:
                logger.exception(
                    'No more retries writing readings {} to file: {}'.format(
                        readings, path))
                raise

