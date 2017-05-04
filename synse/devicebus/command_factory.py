#!/usr/bin/env python
""" A Factory to make new Commands for Synse.

This factory is largely used for convenience and organization. All Command objects
built for Synse should be built through this factory.

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
from threading import Lock

from command import Command
from constants import CommandId


class CommandFactory(object):
    """ Factory for building the supported Synse Commands.
    """

    def __init__(self, counter):
        # typically, we would have this as a class member, but we are making this
        # an instance member here because of its designed use within Flask. as Flask
        # will process each request in a separate thread, we want to be sure that
        # each request thread has access to the same `count` instance for proper
        # incrementation. an instance of `CommandFactory` can be shared in Flask's
        # app config, allowing access to the same count in all threads. since this
        # will be accessed within threads, it should be used in a thread-safe manner.
        self._seq_lock = Lock()
        self._sequencer = counter

    def _get_next_sequence(self):
        """ Get the next command sequence number.

        Returns:
            int: the next sequence number for a Command.
        """
        with self._seq_lock:
            seq = next(self._sequencer)
        return seq

    def get_version_command(self, data):
        """ Generate a Version Command.

        Args:
            data (dict): any key-value data that makes up the command context.

        Returns:
            Command: the generated command for Version
        """
        return Command(CommandId.VERSION, data, self._get_next_sequence())

    def get_scan_command(self, data):
        """ Generate a Scan Command.

        Args:
            data (dict): any key-value data that makes up the command context.

        Returns:
            Command: the generated command for Scan
        """
        return Command(CommandId.SCAN, data, self._get_next_sequence())

    def get_scan_all_command(self, data):
        """ Generate a Scan All Command

        Args:
            data (dict): any key-value data that makes up the command context.

        Returns:
            Command: the generated command for Scan All
        """
        return Command(CommandId.SCAN_ALL, data, self._get_next_sequence())

    def get_read_command(self, data):
        """ Generate a Read Command.

        Args:
            data (dict): any key-value data that makes up the command context.

        Returns:
            Command: the generated command for Read
        """
        return Command(CommandId.READ, data, self._get_next_sequence())

    def get_write_command(self, data):
        """ Generate a Write Command.

        Args:
            data (dict): any key-value data that makes up the command context.

        Returns:
            Command: the generated command for Write
        """
        return Command(CommandId.WRITE, data, self._get_next_sequence())

    def get_power_command(self, data):
        """ Generate a Power Command.

        Args:
            data (dict): any key-value data that makes up the command context.

        Returns:
            Command: the generated command for Power
        """
        return Command(CommandId.POWER, data, self._get_next_sequence())

    def get_asset_command(self, data):
        """ Generate an Asset Command.

        Args:
            data (dict): any key-value data that makes up the command context.

        Returns:
            Command: the generated command for Asset
        """
        return Command(CommandId.ASSET, data, self._get_next_sequence())

    def get_boot_target_command(self, data):
        """ Generate a Boot Target Command.

        Args:
            data (dict): any key-value data that makes up the command context.

        Returns:
            Command: the generated command for Boot Target
        """
        return Command(CommandId.BOOT_TARGET, data, self._get_next_sequence())

    def get_location_command(self, data):
        """ Generate a Location Command.

        Args:
            data (dict): any key-value data that makes up the command context.

        Returns:
            Command: the generated command for Location
        """
        return Command(CommandId.LOCATION, data, self._get_next_sequence())

    def get_chamber_led_command(self, data):
        """ Generate a Chamber LED Command.

        Args:
            data (dict): any key-value data that makes up the command context.

        Returns:
            Command: the generated command for Chamber LED
        """
        return Command(CommandId.CHAMBER_LED, data, self._get_next_sequence())

    def get_led_command(self, data):
        """ Generate an LED Command.

        Args:
            data (dict): any key-value data that makes up the command context.

        Returns:
            Command: the generated command for LED
        """
        return Command(CommandId.LED, data, self._get_next_sequence())

    def get_fan_command(self, data):
        """ Generate a Fan Command.

        Args:
            data (dict): any key-value data that makes up the command context.

        Returns:
            Command: the generated command for Fan
        """
        return Command(CommandId.FAN, data, self._get_next_sequence())

    def get_host_info_command(self, data):
        """ Generate a Host Info Command.

        Args:
            data (dict): any key-value data that makes up the command context.

        Returns:
            Command: the generated command for Host Info
        """
        return Command(CommandId.HOST_INFO, data, self._get_next_sequence())

    def get_retry_command(self, data):
        """ Generate a Retry Command.

        Args:
            data (dict): any key-value data that makes up the command context.

        Returns:
            Command: the generated command for Retry
        """
        return Command(CommandId.RETRY, data, self._get_next_sequence())
