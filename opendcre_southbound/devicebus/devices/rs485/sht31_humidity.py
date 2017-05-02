#!/usr/bin/env python
""" OpenDCRE Southbound RS485 SHT31 Device

    Author: Andrew Cencini
    Date:   10/12/2016

    \\//
     \/apor IO
"""
import logging
import lockfile
import sys

from rs485_device import RS485Device
import opendcre_southbound.strings as _s_
from opendcre_southbound import constants as const
from opendcre_southbound.devicebus.constants import CommandId as cid
from opendcre_southbound.devicebus.response import Response
from opendcre_southbound.errors import OpenDCREException

from pymodbus.client.sync import ModbusSerialClient as ModbusClient
from pymodbus.pdu import ExceptionResponse


logger = logging.getLogger(__name__)


class SHT31Humidity(RS485Device):
    """ Device subclass for SHT31 humidity/temperature sensor using RS485 comms.
    """
    _instance_name = 'sht31'

    def __init__(self, **kwargs):
        super(SHT31Humidity, self).__init__(**kwargs)

        # Sensor specific commands.
        self._command_map[cid.READ] = self._read

        self._lock = lockfile.LockFile(self.serial_lock)

        # the register base is used to map multiple device instances to a device-specific base address
        # such that each device has its own map of registers
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

    def _read(self, command):
        """ Read the data off of a given board's device.

        Args:
            command (Command): the command issued by the OpenDCRE endpoint
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
            raise OpenDCREException('No sensor reading returned from RS485.')
        
        except Exception:
            raise OpenDCREException('Error reading SHT31 humidity sensor (device id: {})'.format(device_id)), None, sys.exc_info()[2]

    def _read_sensor(self):
        """
        
        Returns:

        """
        with self._lock:
            with ModbusClient(method=self.method, port=self.device_name, timeout=self.timeout) as client:
                # read temperature
                result = client.read_holding_registers(self._register_map['temperature_register'], count=1,
                                                       unit=self.unit)
                if result is None:
                    raise OpenDCREException('No response received for SHT31 temperature reading.')
                elif isinstance(result, ExceptionResponse):
                    raise OpenDCREException('RS485 Exception: {}'.format(result))
                temperature = -45 + (175 * ((result.registers[0] * 1.0) / (pow(2, 16) - 1)))

                # read humidity
                result = client.read_holding_registers(self._register_map['humidity_register'], count=1, unit=self.unit)
                if result is None:
                    raise OpenDCREException('No response received for SHT31 humidity reading.')
                elif isinstance(result, ExceptionResponse):
                    raise OpenDCREException('RS485 Exception: {}'.format(result))
                humidity = 100 * ((result.registers[0] * 1.0) / (pow(2, 16) - 1))

                # create client and read registers, composing a reading to return
                return {const.UOM_HUMIDITY: humidity, const.UOM_TEMPERATURE: temperature}
