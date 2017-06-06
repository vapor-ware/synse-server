#!/usr/bin/env python
""" Synse D6F-W10A1 Airflow RS485 Device.

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

from rs485_device import RS485Device
import synse.strings as _s_
from synse import constants as const
from synse.devicebus.constants import CommandId as cid
from synse.devicebus.response import Response
from synse.errors import SynseException

from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.pdu import ExceptionResponse
import conversions.conversions as conversions

logger = logging.getLogger(__name__)

# TODO: Sensor has changed. This is a F660.


class D6FW10A1Airflow(RS485Device):
    """ Device subclass for D6FW10A1 airflow sensor using RS485 comms.

    Reads a 10-bit ADC value from the CEC MCU that maps to 1.00-5.00V,
    then converted to airflow_mm_s. (millimeters per second)
    """
    _instance_name = 'd6f-w10a1'

    def __init__(self, **kwargs):
        super(D6FW10A1Airflow, self).__init__(**kwargs)

        logger.debug('D6FW10A1Airflow kwargs: {}'.format(kwargs))

        # Sensor specific commands.
        self._command_map[cid.READ] = self._read

        # the register base is used to map multiple device instances to a device-specific base address
        # such that each device has its own map of registers
        self.register_base = int(kwargs['base_address'], 16)

        # map of registers needed to read for airflow
        self._register_map = {
            'airflow_reading': self.register_base + 0x0000
        }

        self.board_id = int(kwargs['board_offset']) + int(kwargs['board_id_range'][0])

        self.board_record = dict()
        self.board_record['board_id'] = format(self.board_id, '08x')
        self.board_record['devices'] = [
            {
                'device_id': kwargs['device_id'],
                'device_type': 'airflow',
                'device_info': kwargs.get('device_info', 'cec airflow')
            }
        ]

        # Get remainder from kwargs that is not accounted for.
        self.slave_address = kwargs['device_unit']  # device_unit is the modbus slave address.
        self.device_model = kwargs['device_model']

        logger.debug('D6FW10A1Airflow self: {}'.format(dir(self)))

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
            raise SynseException(
                'Error reading D6F-W10A airflow sensor (device id: {})'.format(
                    device_id)), None, sys.exc_info()[2]

    def _read_sensor(self):
        """ Internal method to get and convert the sensor reading.

        Returns:
            dict: the sensor reading value.
        """
        with self._lock:
            if self.hardware_type == 'emulator':
                with ModbusClient(method=self.method, port=self.device_name, timeout=self.timeout) as client:
                    # read airflow
                    result = client.read_holding_registers(
                        self._register_map['airflow_reading'], count=1, unit=self.unit)
                    if result is None:
                        raise SynseException('No response received for D6F-W10A airflow reading.')
                    elif isinstance(result, ExceptionResponse):
                        raise SynseException('RS485 Exception: {}'.format(result))

                    airflow = result.registers[0]  # pymodbus gives ints not bytes, no conversion needed.

            else:
                # Production
                client = self._create_modbus_client()

                result = client.read_input_registers(self.slave_address, self.register_base,  1)
                airflow = conversions.airflow_d6f_w10a1(result)

            # Return the reading.
            return {const.UOM_AIRFLOW: airflow}
