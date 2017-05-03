#!/usr/bin/env python
""" Constants used for all devicebus components - from implementations to commands.

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


class CommandId(object):
    """ Contains the ID specifications for all supported OpenDCRE commands.
    """
    VERSION = 0x01
    SCAN = 0x02
    SCAN_ALL = 0x03
    READ = 0x04
    WRITE = 0x05
    POWER = 0x06
    ASSET = 0x07
    BOOT_TARGET = 0x08
    LOCATION = 0x09
    CHAMBER_LED = 0x0a
    LED = 0x0b
    FAN = 0x0c
    HOST_INFO = 0x0d
    RETRY = 0x0e

    @classmethod
    def get_command_name(cls, command_id):
        """ Get a human-readable name for a given command ID.

        Args:
            command_id (int): the ID of the command.

        Returns:
            str: the human readable command name
        """
        return {
            cls.VERSION: 'Version',
            cls.SCAN: 'Scan',
            cls.SCAN_ALL: 'Scan All',
            cls.READ: 'Read',
            cls.WRITE: 'Write',
            cls.POWER: 'Power',
            cls.ASSET: 'Asset',
            cls.BOOT_TARGET: 'Boot Target',
            cls.LOCATION: 'Location',
            cls.CHAMBER_LED: 'Chamber LED',
            cls.LED: 'LED',
            cls.FAN: 'Fan',
            cls.HOST_INFO: 'Host Info',
            cls.RETRY: 'Retry'
        }.get(command_id, 'Unknown Command')
