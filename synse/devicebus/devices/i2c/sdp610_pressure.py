#!/usr/bin/env python
""" Synse I2C pressure via SDP610.

    Author: Andrew Cencini
    Date:   10/18/2016

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
from binascii import hexlify

import lockfile

import synse.strings as _s_
from synse import constants as const
from synse.devicebus.constants import CommandId as cid
from synse.devicebus.response import Response
from synse.errors import SynseException
from synse.protocols.i2c_common import i2c_common

from .i2c_device import I2CDevice
from .sdp610_emulator import read_emulator

logger = logging.getLogger(__name__)

POLYNOMIAL = 0x131

# Per data sheet, Section 2
SCALE_FACTOR = 60


class SDP610Pressure(I2CDevice):
    """ Device subclass for thermistor via I2C SDP610 Pressure device.
    """
    _instance_name = 'sdp-610'

    def __init__(self, **kwargs):
        super(SDP610Pressure, self).__init__(**kwargs)

        logger.debug('SDP610Pressure kwargs: {}'.format(kwargs))

        # Sensor specific commands.
        self._command_map[cid.READ] = self._read

        self._lock = lockfile.LockFile(self.serial_lock)

        self.altitude = kwargs['altitude']

        self.channel = int(kwargs['channel'], 16)

        self.board_id = int(kwargs['board_offset']) + int(kwargs['board_id_range'][0])

        self.board_record = dict()
        self.board_record['board_id'] = format(self.board_id, '08x')
        self.board_record['devices'] = [
            {
                'device_id': kwargs['device_id'],
                'device_type': 'pressure',
                'device_info': kwargs.get('device_info', 'CEC pressure')
            }
        ]

        if self.hardware_type == 'production':
            # Configure for 9 bit resolution.
            if i2c_common.configure_differential_pressure(self.channel) != 0:
                raise SynseException(
                    'Failed to configure 9 bit resolution on board id {}. channel {}'.format(
                        self.board_id, self.channel))

        logger.debug('SDP610Pressure self: {}'.format(dir(self)))

    def _read(self, command):
        """ Read the data off of a given board's device.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the read response.
        """
        # get the command data out from the incoming command
        device_id = command.data[_s_.DEVICE_ID]
        device_type_string = command.data[_s_.DEVICE_TYPE_STRING]

        try:
            # validate device to ensure device id and type are ok
            self._get_device_by_id(device_id, device_type_string)

            reading = self._read_sensor()

            if reading is not None:
                return Response(
                    command=command,
                    response_data=reading
                )

            # if we get here, there was no sensor device found, so we must raise
            logger.exception('No response for sensor reading for command: {}'.format(command.data))
            raise SynseException('No sensor reading returned from I2C.')

        except Exception:
            logger.exception('Error reading pressure sensor')
            raise SynseException('Error reading pressure sensor (device id: {})'.format(
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
        data_file = self._get_bg_read_file('{0:04x}'.format(self.channel))
        data = SDP610Pressure.read_sensor_data_file(data_file)
        return {const.UOM_PRESSURE: data[0]}

    def _direct_sensor_read(self):
        """ Internal method for reading data off of the device.

        Returns:
            dict: the pressure reading value.
        """
        with self._lock:
            if self.hardware_type == 'emulator':
                # -- EMULATOR --> test-only code path
                # convert to an int from hex number string read from emulator
                sensor_int = int(hexlify(read_emulator(self.device_name, self.channel)), 16)

                # value is in 16 bit 2's complement
                if sensor_int & 0x8000:
                    sensor_int = (~sensor_int + 1) & 0xFFFF
                    sensor_int = -sensor_int

                return {const.UOM_PRESSURE: sensor_int * 1.0}
            else:
                logger.debug('SDP610Pressure production _read_sensor start: {}')

                reading = i2c_common.read_differential_pressure(self.channel)
                if reading is None:
                    raise SynseException(
                        'Unable to read i2c channel {} on board id {:x}.'.format(
                            self.channel, self.board_id))

                return {const.UOM_PRESSURE: reading}
