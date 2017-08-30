#!/usr/bin/env python
""" Synse SHT31 Humidity RS485 Device.

    Author: Andrew Cencini
    Date:   10/12/2016

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

from flask import request
from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.pdu import ExceptionResponse

import synse.strings as _s_
from synse import constants as const
from synse.devicebus.constants import CommandId as cid
from synse.devicebus.devices.rs485.rs485_device import RS485Device
from synse.devicebus.response import Response
from synse.errors import SynseException
from synse.protocols.conversions import conversions

logger = logging.getLogger(__name__)


class SHT31Humidity(RS485Device):
    """ Device subclass for SHT31 humidity/temperature sensor using RS485 comms.
    """
    _instance_name = 'sht31'

    def __init__(self, **kwargs):
        super(SHT31Humidity, self).__init__(**kwargs)

        logger.debug('SHT31Humidity kwargs: {}'.format(kwargs))

        # Sensor specific commands.
        self._command_map[cid.READ] = self._read

        self._lock = lockfile.LockFile(self.serial_lock)

        # the register base is used to map multiple device instances to a
        # device-specific base address such that each device has its own
        # map of registers
        self.register_base = int(kwargs['base_address'], 16)

        # map of registers needed to read for temp/humidity
        self._register_map = {
            'temperature_register': self.register_base + 0x0000,
            'humidity_register': self.register_base + 0x0001
        }

        self.board_id = int(kwargs['board_offset']) + int(kwargs['board_id_range'][0])

        self.board_record = dict()
        self.board_record['board_id'] = format(self.board_id, '08x')
        self.board_record['devices'] = [
            {
                'device_id': kwargs['device_id'],
                'device_type': 'humidity',
                'device_info': kwargs.get('device_info', 'cec humidity')
            }
        ]

        # Get remainder from kwargs that is not accounted for.
        self.slave_address = kwargs['device_unit']  # device_unit is the modbus slave address.
        self.device_model = kwargs['device_model']

        logger.debug('SHT31Humidity self: {}'.format(dir(self)))

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
            raise SynseException('No sensor reading returned from RS485.')

        except Exception:
            raise SynseException('Error reading SHT31 humidity sensor (device id: {})'.format(
                device_id)), None, sys.exc_info()[2]

    def _read_sensor(self):
        """ Convenience method to return the sensor reading.

        If the sensor is configured to be read indirectly (e.g. from background)
        it will do so -- otherwise, we perform a direct read.
        """
        if self.from_background:
            return self._indirect_sensor_read()
        return self._direct_sensor_read()

    def _indirect_sensor_read(self):
        """Read the sensor data from the intermediary data file.

        FIXME - reading from file is only for the POC. once we can
        confirm that this works and have it stable for the short-term, we
        will need to move on to the longer-term plan of having this done
        via socket.

        Returns:
            dict: the thermistor reading value.
        """
        logger.debug('indirect_sensor_read')

        # If we are not the vec leader we need to redirect this call to the leader.
        # The Synse configuration is supposed to be the same for all vecs in the chamber.
        if not RS485Device.is_vec_leader():
            response = RS485Device.redirect_call_to_vec_leader(request.url)
            return {
                const.UOM_HUMIDITY: response[const.UOM_HUMIDITY],
                const.UOM_TEMPERATURE: response[const.UOM_TEMPERATURE],
            }

        data_file = self._get_bg_read_file(
            str(self.unit), '{0:04d}'.format(self.register_base))
        data = SHT31Humidity.read_sensor_data_file(data_file)
        return {
            const.UOM_TEMPERATURE: data[0],
            const.UOM_HUMIDITY: data[1]
        }

    def _direct_sensor_read(self):
        """ Internal method for reading data off of the SHT31 Humidity device.

        Returns:
            dict: the temperature and humidity reading values.
        """
        with self._lock:
            if self.hardware_type == 'emulator':
                with ModbusClient(method=self.method, port=self.device_name,
                                  timeout=self.timeout) as client:

                    # read temperature
                    result = client.read_holding_registers(
                        self._register_map['temperature_register'],
                        count=1,
                        unit=self.unit)

                    if result is None:
                        raise SynseException(
                            'No response received for SHT31 temperature reading.')
                    elif isinstance(result, ExceptionResponse):
                        raise SynseException('RS485 Exception: {}'.format(result))
                    temperature = conversions.temperature_sht31_int(result.registers[0])

                    # read humidity
                    result = client.read_holding_registers(
                        self._register_map['humidity_register'],
                        count=1,
                        unit=self.unit)

                    if result is None:
                        raise SynseException(
                            'No response received for SHT31 humidity reading.')
                    elif isinstance(result, ExceptionResponse):
                        raise SynseException('RS485 Exception: {}'.format(result))
                    humidity = conversions.humidity_sht31_int(result.registers[0])

                    # Return the reading.
                    return {const.UOM_HUMIDITY: humidity, const.UOM_TEMPERATURE: temperature}

            elif self.hardware_type == 'production':
                # Production
                client = self.create_modbus_client()
                result = client.read_input_registers(self.slave_address, self.register_base, 2)
                temperature = conversions.temperature_sht31(result)
                humidity = conversions.humidity_sht31(result)

                return {const.UOM_HUMIDITY: humidity, const.UOM_TEMPERATURE: temperature}

            else:
                raise SynseException(RS485Device.HARDWARE_TYPE_UNKNOWN.format(
                    self.hardware_type))
