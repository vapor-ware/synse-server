#!/usr/bin/env python
""" OpenDCRE Southbound LAN Devices

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


class LANDevice(DevicebusInterface):
    """ The base class for all LAN-based devicebus interfaces.
    """

    def __init__(self):
        super(LANDevice, self).__init__()

    @classmethod
    def register(cls, devicebus_config, app_config, app_cache):
        raise NotImplementedError
