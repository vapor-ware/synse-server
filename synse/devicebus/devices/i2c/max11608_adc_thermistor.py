#!/usr/bin/env python
""" Synse I2C thermistor via MAX11608 ADC

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
import struct
import sys

import lockfile

import synse.strings as _s_
from synse import constants as const
from synse.devicebus.constants import CommandId as cid
from synse.devicebus.devices.i2c.i2c_device import I2CDevice
from synse.devicebus.devices.i2c.max11608_adc_emulator import read_emulator
from synse.devicebus.response import Response
from synse.errors import SynseException
from synse.protocols.conversions import conversions
from synse.protocols.i2c_common import i2c_common

logger = logging.getLogger(__name__)


class Max11608Thermistor(I2CDevice):
    """ Device subclass for thermistor via MAX11608 I2C ADC.
    """
    _instance_name = 'max-11608'

    def __init__(self, **kwargs):
        super(Max11608Thermistor, self).__init__(**kwargs)
        logger.debug('Max11608Thermistor kwargs: {}'.format(kwargs))

        # Sensor specific commands.
        self._command_map[cid.READ] = self._read

        self._lock = lockfile.LockFile(self.serial_lock)

        self.channel = int(kwargs['channel'], 16)

        self.board_id = int(kwargs['board_offset']) + int(kwargs['board_id_range'][0])

        self.board_record = dict()
        self.board_record['board_id'] = format(self.board_id, '08x')
        self.board_record['devices'] = [
            {
                'device_id': kwargs['device_id'],
                'device_type': 'temperature',
                'device_info': kwargs.get('device_info', 'CEC temperature')
            }
        ]

        logger.debug('Max11608Thermistor self: {}'.format(self))

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
            logger.error('No response for sensor reading for command: {}'.format(command.data))
            raise SynseException('No sensor reading returned from I2C.')

        except Exception:
            raise SynseException('Error reading temperature sensor (device id {})'.format(
                device_id)), None, sys.exc_info()[2]

    def _read_sensor(self):
        """ Internal method for reading data off of the device.

        Returns:
            dict: the thermistor reading value.
        """
        with self._lock:
            if self.hardware_type == 'emulator':
                # -- EMULATOR --> test-only code path
                raw = read_emulator(self.device_name, self.channel)
                # raw is an int like 0.
                # Conversion takes packed bytes.
                # Get packed bytes for the conversion.
                packed = struct.pack('>H', raw)
                return {const.UOM_TEMPERATURE: conversions.thermistor_max11608_adc(packed)}

            # Channel is zero based in the synse config.
            # Read channel + 1 thermistors and return the last one read in the reading.
            readings = i2c_common.read_thermistors(self.channel + 1)
            return {const.UOM_TEMPERATURE: readings[self.channel]}
