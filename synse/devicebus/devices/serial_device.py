#!/usr/bin/env python
""" Synse Serial Device Base

    Author: Erick Daniszewski
    Date:   09/15/2016

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
import os
from synse.devicebus.devices.base import DevicebusInterface

logger = logging.getLogger(__name__)


class SerialDevice(DevicebusInterface):
    """ The base class for all Serial-based devicebus interfaces.
    """

    def __init__(self, lock_path):
        super(SerialDevice, self).__init__()
        self.serial_lock = lock_path

    @classmethod
    def register(cls, devicebus_config, app_config, app_cache):
        raise NotImplementedError

    @staticmethod
    def read_sensor_data_file(path):
        """Read in data from a sensor data file. The file will have one data
        point per line.
        :param path: The path of the file to read.
        :returns: A list of data. Some coercion is done here to try to get the
        data types correct."""
        logger.debug('reading sensor data from: {}'.format(path))

        # TODO - might need a lock around here?
        try:
            with open(path, 'r') as f:
                data = f.read()
        except Exception as e:
            logger.exception(e)
            raise

        data = data.split()
        for i, _ in enumerate(data):
            if data[i] == 'null':
                data[i] = None  # JSON null to python None.
            else:
                # See if this is a float, otherwise treat as a string.
                try:
                    data[i] = float(data[i])  # Precision is sensor specific.
                except (TypeError, ValueError):
                    pass  # Ignore.
        return data
