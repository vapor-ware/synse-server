#!/usr/bin/env python
""" The base interface for all devicebus subclasses.

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

import json
import logging
from uuid import uuid4 as uuid

from synse.devicebus.constants import CommandId
from synse.errors import CommandNotSupported, SynseException

logger = logging.getLogger(__name__)


class DevicebusInterface(object):
    """ Base interface for all Devicebus objects supported by Synse.

    Primarily, this defines some common methods that can be used or overridden
    by its subclasses. Of note, the `_instance_name` member should be used by
    terminal subclasses to specify the name of the device that class represents.
    This is particularly useful for identifying individual device types, as is
    done for I2C and RS485 devices.

    A `handle` method is also defined and should NOT be overridden. It provides
    the device logic to process an incoming Command and dispatch it to the Device's
    appropriate handler method, if it exists.

    Finally, a `register` method is defined but not implemented. Device
    registration is dependent on the type of devicebus instance being registered,
    therefore it is left to the specific devicebus instance to define its own
    register method.
    """
    _instance_name = None
    proto = None

    def __init__(self):
        # map command ids to the devicebus methods which will be used to operate
        # on those methods. each subclass should define its own _command_map. if
        # a supported command id is missing from the command map, the default
        # behavior is to consider that command unsupported for the given devicebus
        # interface and raise an exception.
        self._command_map = {}

        # each device will have its own UUID. this id is used internally for quicker
        # lookups when routing commands to specific devices.
        self.device_uuid = uuid()

        # defines a flag that can be checked to see whether the device is configured
        # to operate directly (e.g. via the synse application) or indirectly
        # (e.g. via a background process). this flag is set on device registration
        # if the device is configured with the "from_background" field (default
        # False).
        self.from_background = False

        # the rack id for which the device resides on. initialized as None here, but
        # when the subclasses are registered/initialized, they will provide the
        # actual rack_id
        self.rack_id = None

    @classmethod
    def register(cls, devicebus_config, app_config, app_cache):
        """ Register a new instance of the Devicebus class.
        """
        raise NotImplementedError

    def handle(self, command):
        """ Handle an incoming Synse command.

        Args:
            command (Command): the incoming command object to dispatch to the
                appropriate command handler for the Devicebus object.

        Returns:
            Response: the response data for the requested Command.

        Raises:
            CommandNotSupported: The given command does not have a corresponding
                handler defined for the Devicebus instance - this means that the
                given instance does not support any actions for that command.
        """
        cmd_fn = self._command_map.get(command.cmd_id, None)
        if cmd_fn is None:
            raise CommandNotSupported('Command "{}" not supported for {}'.format(
                CommandId.get_command_name(command.cmd_id),
                self.__class__.__name__
            ))

        response = cmd_fn(command)

        return response

    def _get_device_by_id(self, device_id, device_type_string):
        """ Get a device that can be used for device-relative commands.

        When device_id is numeric, this can be used to validate the device_id and
        type match, and get its device entry for use elsewhere.  When its a string
        value, we validate the device_info and device_type match what is given, and
        return the device entry.

        Args:
            device_id (str | int): the device_id to look up.
            device_type_string (str): the type of the device that device_id should
                be represented by in the board record.

        Returns:
            dict: the device entry from the board_record corresponding to this device.
        """
        if isinstance(device_id, int):
            # look up device by device_id and return its record if found
            for device in self.board_record['devices']:
                if (format(device_id, '04x')) == device['device_id'] and \
                        device_type_string == device['device_type']:
                    return device

        elif isinstance(device_id, basestring):
            # if this is a non-numeric device_id, we'll look for the device by the string
            # id and return its record
            for device in self.board_record['devices']:
                if 'device_info' in device:
                    if device_id.lower() == device['device_info'].lower() and \
                            device_type_string == device['device_type']:
                        return device

        # if we get here, numeric and string device_id search has failed, so raise exception
        raise SynseException(
            'Device ID {} not found in board record for {}.'.format(device_id, self.board_id)
        )

    def _get_bg_path(self, *device_ident):
        """
        Elements in device_ident must be passed in as strings.
        """
        device_identity = '/'.join(device_ident)
        return '/synse/sensors/{proto}/{rack}/{model}/{id}'.format(
            proto=self.proto,
            rack=self.rack_id,
            model=self._instance_name,
            id=device_identity
        )

    def _get_bg_read_file(self, *device_ident):
        """ Convenience method for the background read POC

        TODO -- will need to change once this is proven out and the real
        implementation work begins.

        This method is used to get the location of the file that
        is used as the interface between the background process
        and the device.

        Args:
            *device_ident: a tuple of device identity string parameters that
                will be concatenated (in order) to generate the
                identity for the device. while the identity format should
                be the same for all devices of a given protocol, this is
                kept general so it can apply to devices of any protocol.
        """
        result = '/'.join((self._get_bg_path(*device_ident), 'read'))
        logger.debug('bg_file: {}'.format(result))
        return result

    def _get_bg_write_file(self, *device_ident):
        """ Convenience method for the background write POC

        TODO -- will need to change once this is proven out and the real
        implementation work begins.

        This method is used to get the location of the file that
        is used as the interface between the background process
        and the device.

        Args:
            *device_ident: a tuple of device identity parameters that
                will be concatenated (in order) to generate the
                identity for the device. while the identity format should
                be the same for all devices of a given protocol, this is
                kept general so it can apply to devices of any protocol.
        """
        return '/'.join((self._get_bg_path(*device_ident), 'write'))

    @classmethod
    def get_device_config(cls, devicebus_config):
        """ Get the device configuration as specified in the devicebus_config dict
        (e.g., either in-line or in a separate file).

        Args:
            devicebus_config (dict): configuration dictionary loaded in by Synse
                which specifies the configurations for the device.

        Returns:
            dict: the devicebus-specific configuration
            None: if failed to load the configuration
        """
        device_config = None
        try:
            # configuration is defined in separate file.
            if 'from_config' in devicebus_config:
                with open(devicebus_config['from_config']) as f:
                    device_config = json.load(f)

            # configuration is defined inline of the current file.
            elif 'config' in devicebus_config:
                device_config = devicebus_config['config']

            # otherwise, there is no valid config device specified
            else:
                logger.error(
                    'No valid device config found for {} configuration. Requires either the '
                    '"from_config" field or the "config" field.'.format(cls.__name__)
                )

        except (OSError, IOError) as e:
            logger.error('Error opening / reading specified configuration file: {}'.format(
                devicebus_config['from_config']))
            logger.exception(e)
        except Exception as e:
            logger.error('Unexpected failure when attempting to get devicebus configuration.')
            logger.exception(e)

        return device_config

    @staticmethod
    def validate_app_state(app_cache):
        """ Common method for validation of the application state that is passed to
        the register method.

        This does not return anything, but will raise an exception if the app state
        is incorrect.

        Args:
            app_cache (tuple): a 2-tuple where the first item is a mutable dictionary
                which is used to map a DevicebusInterfaces' UUID to the DevicebusInterface
                instance and the second item is a mutable dictionary which maps the
                board id(s) for a given DevicebusInterface to its instance. These mutable
                structures are used as lookup tables by the Flask application.
        """
        if len(app_cache) != 2:
            raise ValueError(
                'App cache does not contain 2 collections: {}'.format(app_cache)
            )

    @classmethod
    def get_instance_name(cls):
        """Get the instance name of the device."""
        return cls._instance_name