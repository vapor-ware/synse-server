#!/usr/bin/env python
""" Synse lock for RCI3525 door locks. I2C protocol.

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
import sys

import lockfile

import synse.strings as _s_
from synse.devicebus.constants import CommandId as cid
from synse.devicebus.response import Response
from synse.errors import SynseException
from synse.protocols.i2c_common import i2c_common

from .i2c_device import I2CDevice


logger = logging.getLogger(__name__)


class RCI3525Lock(I2CDevice):
    """ Device subclass for the RCI 3525 door lock.
    """
    _instance_name = 'rci-3525'

    def __init__(self, **kwargs):
        super(RCI3525Lock, self).__init__(**kwargs)

        logger.debug('RCI3525Lock kwargs: {}'.format(kwargs))

        # Sensor specific commands.
        self._command_map[cid.READ] = self._read
        self._command_map[cid.LOCK] = self._lock_function

        self._lock = lockfile.LockFile(self.serial_lock)

        self.channel = int(kwargs['channel'], 16)

        self.board_id = int(kwargs['board_offset']) + int(kwargs['board_id_range'][0])

        self.board_record = dict()
        self.board_record['board_id'] = format(self.board_id, '08x')
        self.board_record['devices'] = [
            {
                'device_id': kwargs['device_id'],
                'device_type': 'lock',
                'device_info': kwargs.get('device_info', 'Door Lock')
            }
        ]

        if self.hardware_type != 'production':
            raise ValueError(
                'Only production hardware is supported initially. '
                'We may add emulator support later.')

        self.lock_number = int(kwargs['lock_number'])
        if not 1 <= self.lock_number <= 12:
            raise ValueError('Lock number {} out of range 1-12.'.format(self.lock_number))

        logger.debug('RCI3525Lock self: {}'.format(dir(self)))

    def _read(self, command):
        """ Read the data off of a given board's device.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the read response.
        """
        # Get the command data out from the incoming command.
        device_id = command.data[_s_.DEVICE_ID]
        device_type_string = command.data[_s_.DEVICE_TYPE_STRING]

        try:
            # Validate device to ensure device id and type are ok.
            self._get_device_by_id(device_id, device_type_string)

            reading = self._read_sensor()

            if reading is not None:
                return Response(
                    command=command,
                    response_data=reading
                )

            # If we get here, there was no sensor device found, so we must raise.
            logger.exception('No response for sensor reading for command: {}'.format(command.data))
            raise SynseException('No sensor reading returned from I2C.')

        except Exception:
            logger.exception()
            raise SynseException('Error reading lock (device id: {})'.format(
                device_id)), None, sys.exc_info()[2]

    def _read_sensor(self):
        """ Convenience method to return the sensor reading.

        If the sensor is configured to be read indirectly (e.g. from background)
        it will do so -- otherwise, we perform a direct read.
        """
        if self.from_background:
            return self.indirect_sensor_read()
        return self._direct_sensor_read()

    def indirect_sensor_read(self):
        """Read the sensor data from the intermediary data file.

        FIXME - reading from file is only for the POC. once we can
        confirm that this works and have it stable for the short-term, we
        will need to move on to the longer-term plan of having this done
        via socket.

        Returns:
            dict: the thermistor reading value.
        """
        logger.debug('indirect_sensor_read')
        raise NotImplementedError('Indirect sensors reads are coming in the future.')
        # Code below will either be used or deleted for indirect sensor reads.
        # data_file = self._get_bg_read_file('{0:04x}'.format(self.lock_number))
        # data = RCI3525Lock.read_sensor_data_file(data_file)
        # return {'lock_status': data[0]}

    def _direct_sensor_read(self):
        """ Internal method for reading data off of the device.

        Returns:
            dict: Key is lock_status. Data are:
                0 - Electrically unlocked and mechanically unlocked.
                1 - Electrically unlocked and mechanically locked.
                2 - Electrically locked and mechanically unlocked.
                3 - Electrically locked and mechanically locked.
        """
        with self._lock:
            logger.debug('RCI3525Lock _direct_sensor_read: {}')
            reading = i2c_common.lock_status(self.lock_number)
            return {'lock_status': reading}

    # Needs to be called something other than _lock since that is self._lock is
    # a lockfile in subclasses of I2CDevice.
    def _lock_function(self, command):
        """ Read or write the lock state.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the lock response.
        """
        # Get the command data out from the incoming command.
        device_id = command.data[_s_.DEVICE_ID]
        device_type_string = command.data[_s_.DEVICE_TYPE_STRING]
        action = command.data[_s_.ACTION]

        try:
            # Validate device to ensure device id and type are ok.
            self._get_device_by_id(device_id, device_type_string)

            reading = {}  # Sets do not return a reading, just a status code.
            if action is None or action == 'status':
                reading = self._read_sensor()

            elif action == 'lock':
                i2c_common.lock_lock(self.lock_number)

            elif action == 'unlock':
                i2c_common.lock_unlock(self.lock_number)

            elif action == 'momentary_unlock':
                i2c_common.lock_momentary_unlock(self.lock_number)

            else:
                raise SynseException('Invalid action provided for lock control.')

            return Response(
                command=command,
                response_data=reading,
            )

        except Exception:
            logger.exception('Error reading lock. Raising SynseException.')
            raise SynseException('Error reading lock (device id: {})'.format(
                device_id)), None, sys.exc_info()[2]
