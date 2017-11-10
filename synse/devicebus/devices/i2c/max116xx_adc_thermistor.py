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
from synse.devicebus.devices.i2c.max116xx_adc_emulator import read_emulator
from synse.devicebus.response import Response
from synse.errors import SynseException
from synse.protocols.conversions import conversions
from synse.protocols.i2c_common import i2c_common

logger = logging.getLogger(__name__)


class Max116xxThermistor(I2CDevice):
    """Base device class for MAX 116xx Analog to Digital Converters with
    thermistors plugged in."""

    _instance_name = None  # Must be overridden in a subclass.

    def __init__(self, **kwargs):
        super(Max116xxThermistor, self).__init__(**kwargs)
        logger.debug('Max116xxThermistor kwargs: {}'.format(kwargs))

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

        logger.debug('Max116xxThermistor self: {}'.format(self))

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

            # If we get here, there was no sensor device found, so we must raise.
            logger.error('No response for sensor reading for command: {}'.format(command.data))
            raise SynseException('No sensor reading returned from I2C.')

        except Exception:
            logger.exception()
            raise SynseException('Error reading temperature sensor (device id {})'.format(
                device_id)), None, sys.exc_info()[2]

    def _read_sensor(self):
        """ Convenience method to return the sensor reading.

        If the sensor is configured to be read indirectly (e.g. from background)
        it will do so -- otherwise, we perform a direct read.
        """
        logger.debug('self.from_background: {}'.format(self.from_background))
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
        data = Max11608Thermistor.read_sensor_data_file(data_file)
        logger.debug('data: {}'.format(data))
        return {const.UOM_TEMPERATURE: data[0]}

    def _direct_sensor_read(self):
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

            elif self.hardware_type == 'production':
                # Channel is zero based in the synse config.
                # Read channel + 1 thermistors and return the last one read in the reading.
                readings = i2c_common.read_thermistors(
                    self.channel + 1, type(self)._instance_name)
                return {const.UOM_TEMPERATURE: readings[self.channel]}

            else:
                raise SynseException('Unknown hardware type {}.', self.hardware_type)


class Max11608Thermistor(Max116xxThermistor):
    """Device class for a MAX11608 Analog to Digital Converter with a
    thermistor plugged in.
    """
    _instance_name = 'max-11608'

    def __init__(self, **kwargs):
        super(Max11608Thermistor, self).__init__(**kwargs)


class Max11610Thermistor(Max116xxThermistor):
    """Device class for a MAX11610 Analog to Digital Converter with a
    thermistor plugged in.
    """
    _instance_name = 'max-11610'

    def __init__(self, **kwargs):
        super(Max11610Thermistor, self).__init__(**kwargs)
