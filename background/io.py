#!/usr/bin/env python
""" Helpers to handle the file writes for sensor reads.

    Author: Erick Daniszewski
    Date:   19 July 2017

    \\//
     \/apor IO
"""

import os

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


def write_all_from_dict(device_name, timestamp, readings):
    """
    """
    for addr, data in readings:
        write(
            device_name=device_name,
            device_address=addr,
            timestamp=timestamp,
            data=data
        )
