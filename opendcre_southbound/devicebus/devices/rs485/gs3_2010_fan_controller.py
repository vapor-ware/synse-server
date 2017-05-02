#!/usr/bin/env python
""" OpenDCRE Southbound GS3-2010 Fan Control RS485 Device

    Author: Andrew Cencini
    Date:   10/13/2016

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

# establish constants for min/max fan speeds for this unit
MIN_FAN_SPEED_RPM = 0
MAX_FAN_SPEED_RPM = 1200


class GS32010Fan(RS485Device):
    """ Device subclass for GS3-2010 fan controller using RS485 comms.

    FIXME: Currently reads a raw speed_rpm from RS485, will need to implement proper read/control shortly.
    """
    _instance_name = 'gs3-2010'

    def __init__(self, **kwargs):
        super(GS32010Fan, self).__init__(**kwargs)

        # Sensor specific commands.
        self._command_map[cid.READ] = self._read
        self._command_map[cid.FAN] = self._fan

        self._lock = lockfile.LockFile(self.serial_lock)

        # the register base is used to map multiple device instances to a device-specific base address
        # such that each device has its own map of registers
        self.register_base = int(kwargs['base_address'], 16)

        # map of registers needed to read for fan control
        # FIXME: the real register map is likely extensive for the fan controller - this is temp for testing
        self._register_map = {
            'speed_rpm': self.register_base + 0x0000
        }

        self.board_id = int(kwargs['board_offset']) + int(kwargs['board_id_range'][0])

        self.board_record = dict()
        self.board_record['board_id'] = format(self.board_id, '08x')
        self.board_record['devices'] = [
            {
                'device_id': kwargs['device_id'], 
                'device_type': 'vapor_fan',
                'device_info': kwargs.get('device_info', 'chamber fan control')
            }
        ]

    def _fan(self, command):
        """ Fan speed control command for a given board and device.

        Args:
            command (Command): the command issued by the OpenDCRE endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the fan response.
        """
        # get the command data out from the incoming command
        device_id = command.data[_s_.DEVICE_ID]
        fan_speed = int(command.data[_s_.FAN_SPEED])

        # FIXME: override because main_blueprint doesn't distinguish between 'fan_speed' and 'vapor_fan'
        device_type_string = const.DEVICE_VAPOR_FAN

        try:
            # validate device to ensure device id and type are ok
            self._get_device_by_id(device_id, device_type_string)

            reading = self._fan_control(action='set_speed', speed_rpm=fan_speed)

            if reading is not None:
                return Response(
                    command=command,
                    response_data=reading
                )

            # if we get here, there was no vapor_fan device found, so we must raise
            logger.error('No response for fan control for command: {}'.format(command.data))
            raise OpenDCREException('No fan control response returned from RS485.')
        
        except Exception:
            raise OpenDCREException('Error controlling GS3-2010 fan controller (device id: {})'.format(device_id)), None, sys.exc_info()[2]

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

        if device_type_string not in [const.DEVICE_VAPOR_FAN, const.DEVICE_FAN_SPEED]:
            # this command is not for us
            raise OpenDCREException('Incorrect device type "{}" for GS3-2010 fan.'.format(device_type_string))

        # FIXME: override because main_blueprint doesn't distinguish between 'fan_speed' and 'vapor_fan'
        device_type_string = const.DEVICE_VAPOR_FAN

        try:
            # validate device to ensure device id and type are ok
            self._get_device_by_id(device_id, device_type_string)

            reading = self._fan_control(action='status')

            if reading is not None:
                return Response(
                    command=command,
                    response_data=reading
                )

            # if we get here, there was no vapor_fan device found, so we must raise
            logger.error('No response for fan control for command: {}'.format(command.data))
            raise OpenDCREException('No fan control response returned from RS485.')

        except Exception:
            raise OpenDCREException('Error controlling GS3-2010 fan controller (device id: {})'.format(device_id)), None, sys.exc_info()[2]

    def _fan_control(self, action='status', speed_rpm=None):
        """

        Args:
            action:
            speed_rpm:

        Returns:

        """
        with self._lock:
            if action == 'set_speed' and speed_rpm is not None:
                # set fan speed by writing to register
                # FIXME (etd): should this be MIN > speed_rpm > MAX?
                if MIN_FAN_SPEED_RPM < speed_rpm > MAX_FAN_SPEED_RPM:
                    raise OpenDCREException(
                        'Invalid speed setting {} for GS3-2010 fan control - must be between {} and {}'.format(
                            speed_rpm, MIN_FAN_SPEED_RPM, MAX_FAN_SPEED_RPM)
                    )
                with ModbusClient(method=self.method, port=self.device_name, timeout=self.timeout) as client:
                    # write speed
                    result = client.write_registers(self._register_map['speed_rpm'], [speed_rpm], unit=self.unit)
                    if result is None:
                        raise OpenDCREException('No response received for GS3-2010 fan control.')
                    elif isinstance(result, ExceptionResponse):
                        raise OpenDCREException('RS485 Exception: {}'.format(result))

            # in all cases, read out / compute the fan_speed from RS485
            with ModbusClient(method=self.method, port=self.device_name, timeout=self.timeout) as client:
                # read speed
                result = client.read_holding_registers(self._register_map['speed_rpm'], count=1, unit=self.unit)
                if result is None:
                    raise OpenDCREException('No response received for GS3-2010 fan control.')
                elif isinstance(result, ExceptionResponse):
                    raise OpenDCREException('RS485 Exception: {}'.format(result))

                # create client and read registers, composing a reading to return
                return {const.UOM_VAPOR_FAN: result.registers[0]}
