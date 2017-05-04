#!/usr/bin/env python
""" Synse Serial Devices

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
from base import DevicebusInterface


class SerialDevice(DevicebusInterface):
    """ The base class for all Serial-based devicebus interfaces.
    """

    def __init__(self, lock_path):
        super(SerialDevice, self).__init__()
        self.serial_lock = lock_path

    @classmethod
    def register(cls, devicebus_config, app_config, app_cache):
        raise NotImplementedError
