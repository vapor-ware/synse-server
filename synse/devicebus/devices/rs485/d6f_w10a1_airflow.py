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


logger = logging.getLogger(__name__)


class D6FW10A1Airflow(RS485Device):
    """ Device subclass for D6FW10A1 airflow sensor using RS485 comms.

    Reads a 10-bit ADC value from the CEC MCU that maps to 1.00-5.00V,
    then converted to airflow_m_s.
    """
    _instance_name = 'd6f-w10a1'

    def __init__(self, **kwargs):
        super(D6FW10A1Airflow, self).__init__(**kwargs)

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
            raise SynseException('Error reading D6F-W10A airflow sensor (device id: {})'.format(device_id)), None, sys.exc_info()[2]

    def _read_sensor(self):
        """ Internal method to get and convert the sensor reading.

        Returns:
            dict: the sensor reading value.
        """
        with self._lock:
            with ModbusClient(method=self.method, port=self.device_name, timeout=self.timeout) as client:
                # read airflow
                result = client.read_holding_registers(self._register_map['airflow_reading'], count=1, unit=self.unit)
                if result is None:
                    raise SynseException('No response received for D6F-W10A airflow reading.')
                elif isinstance(result, ExceptionResponse):
                    raise SynseException('RS485 Exception: {}'.format(result))
                airflow = (result.registers[0] * 0.01)  # FIXME: temporarily scale values from 0..399 to V (0-based)

                # FIXME: ***these will need to be tweaked based on the actual hardware register values***
                if 0.00 <= airflow <= 0.93:
                    #     VOLTS        FLOW     STEP RATE
                    # 1.00 .. 1.93 :  0 .. 2    200/93
                    airflow *= (200.0 / 93.0)
                elif 0.94 <= airflow <= 2.23:
                    # 1.94 .. 3.23 :  2 .. 4    200/129
                    airflow = ((airflow - 0.95) * (200.0 / 129.0)) + 2.0
                elif 2.24 <= airflow <= 3.25:
                    # 3.24 .. 4.25 :  4 .. 6    200/101
                    airflow = ((airflow - 2.24) * (200.0 / 101.0)) + 4.0
                elif 3.26 <= airflow <= 3.73:
                    # 4.26 .. 4.73 :  6 .. 8    200/47
                    airflow = ((airflow - 3.26) * (200.0 / 47.0)) + 6.0
                elif 3.74 <= airflow < 4.00:
                    # 4.74 .. 5.00 :  8 .. 10   26.0/200
                    airflow = ((airflow - 3.74) * (200.0 / 26.0)) + 8.0
                else:
                    raise SynseException('Invalid raw reading for airflow sensor: {}'.format(airflow))

                # create client and read registers, composing a reading to return
                return {const.UOM_AIRFLOW: airflow}
