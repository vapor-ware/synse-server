#!/usr/bin/env python
""" Synse I2C Device

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
import lockfile
import logging

from synse import constants as const
from synse.devicebus.constants import CommandId as cid
from synse.devicebus.response import Response
from synse.devicebus.devices.serial_device import SerialDevice
from synse.version import __api_version__, __version__


logger = logging.getLogger(__name__)


class I2CDevice(SerialDevice):
    """ Base class for all I2C device implementations.
    """
    def __init__(self, **kwargs):
        super(I2CDevice, self).__init__(lock_path=kwargs['lockfile'])

        self.hardware_type = kwargs.get('hardware_type', 'unknown')

        self.device_name = kwargs['device_name']
        self.rack_id = kwargs['rack_id']
        self.unit = kwargs.get('device_unit', 0)

        self._lock = lockfile.LockFile(self.serial_lock)

        # initialize board record -- all subclasses should implement their
        # own board record.
        self.board_record = None

        # Common I2C commands.
        self._command_map = {
            cid.SCAN: self._scan,
            cid.SCAN_ALL: self._scan_all,
            cid.VERSION: self._version,
        }

    def __str__(self):
        return '<{} (rack: {}, board: {:08x})>'.format(self.__class__.__name__, self.rack_id, self.board_id)

    def __repr__(self):
        return self.__str__()

    @classmethod
    def register(cls, devicebus_config, app_config, app_cache):
        """ Register I2C devices.

        Args:
            devicebus_config (dict): a dictionary containing the devicebus configurations
                for I2C. within this dict is a list or reference to the actual configs
                for the I2C devices themselves.
            app_config (dict): Flask application config, where application-wide
                configurations and constants are stored.
            app_cache (tuple): a tuple which contains the mutable structures
                which make up the app's device cache and lookup tables. The first
                item is a mapping of UUIDs to the devices registered here. The second
                item is a collection of "single board devices". All collections are
                mutated by this method to add all devices which are successfully
                registered, making them available to the Flask app.
        """
        cls.validate_app_state(app_cache)
        device_cache, single_board_devices = app_cache

        device_config = cls.get_device_config(devicebus_config)
        if not device_config:
            raise ValueError('Unable to get configuration for device - unable to register.')

        # sensor-specific configuration -- these should be made available to all registered I2C devices
        _altitude_m = device_config.get('altitude', 0)  # default: 0 meters

        # now, for each device in i2c devices, we create a device instance
        if 'racks' in device_config:
            for rack in device_config['racks']:
                for i2c_device in rack['devices']:
                    i2c_device['rack_id'] = rack['rack_id']
                    i2c_device['board_offset'] = app_config['I2C_BOARD_OFFSET'].next()
                    i2c_device['board_id_range'] = device_config.get('board_id_range', const.I2C_BOARD_RANGE)
                    i2c_device['hardware_type'] = rack.get('hardware_type', 'unknown')
                    i2c_device['device_name'] = rack['device_name']
                    i2c_device['lockfile'] = rack['lockfile']

                    # sensor configurations
                    i2c_device['altitude'] = _altitude_m

                    # since we are unable to import subclasses (circular import), but
                    # we still need to initialize a subclassed device interface, we
                    # match the configured 'device_model' with the '_instance_name' of
                    # all subclasses to determine the correct subclass at runtime.
                    device_model = {
                        klass._instance_name: klass for klass in cls.__subclasses__()
                    }.get(i2c_device['device_model'].lower())

                    if device_model:
                        try:
                            device_instance = device_model(**i2c_device)
                        except Exception as e:
                            logger.error('Error initializing device: ')
                            logger.exception(e)
                            raise

                        # cache reference to device
                        device_cache[device_instance.device_uuid] = device_instance
                        single_board_devices[device_instance.board_id] = device_instance

                    else:
                        logger.warning(
                            'Unsupported device model ({}) found. Skipping registration.'.format(
                                i2c_device['device_model'])
                        )

        else:
            # FIXME: In this case, do we raise an exception?
            logger.error(
                'Device configuration should specify "racks", but does not! Unable to '
                'register I2C devices.'
            )

    def _scan(self, command):
        """ Common scan functionality for all I2C devices.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the scan response.
        """
        boards = [] if self.board_record is None else [self.board_record]
        return Response(
            command=command,
            response_data={
                'boards': boards
            }
        )

    def _scan_all(self, command):
        """ Common scan functionality for all I2C devices.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the scan all response.
        """
        boards = [] if self.board_record is None else [self.board_record]
        scan_results = {'racks': [
            {
                'rack_id': self.rack_id,
                'boards': boards
            }
        ]}

        return Response(
            command=command,
            response_data=scan_results
        )

    def _version(self, command):
        """ Get the version information for a given board.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the version response.
        """
        return Response(
            command=command,
            response_data={
                'api_version': __api_version__,
                'synse_version': __version__,
                'firmware_version': 'Synse I2C Bridge v1.0'
            }
        )
