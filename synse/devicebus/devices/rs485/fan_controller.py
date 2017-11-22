#!/usr/bin/env python
""" Synse Base Fan Controller RS485 Device.

    \\//
     \/apor IO

-------------------------------
Copyright (C) 2017  Vapor IO

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


logger = logging.getLogger(__name__)


class FanController(RS485Device):
    """Common functionality for fan controllers."""

    def __init__(self, **kwargs):
        """Base class for fan controller (vapor_fan) devices."""
        super(FanController, self).__init__(**kwargs)

        # Sensor specific commands.
        self._command_map[cid.READ] = self._read
        self._command_map[cid.FAN] = self._fan

        self._lock = lockfile.LockFile(self.serial_lock)

        # the register base is used to map multiple device instances to a device-specific
        # base address such that each device has its own map of registers
        self.register_base = int(kwargs['base_address'], 16)

        # Map of registers needed to read for fan control.
        # The full production register map does not lend itself
        # well here for the limited functionality we need for synse.
        self._register_map = None

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

        # Get remainder from kwargs that is not accounted for.
        self.slave_address = kwargs['device_unit']  # device_unit is the modbus slave address.
        self.device_model = kwargs['device_model']

    # Interface that must be implemented in sub classes.

    def _get_direction(self):
        """Production only direction reads from gs3_2010_fan (vapor_fan).
        :returns: String forward or reverse."""
        raise NotImplementedError('Must be implemented in subclass')

    def _get_rpm(self):
        """Production only rpm reads from gs3_2010_fan (vapor_fan).
        :returns: Integer rpm."""
        raise NotImplementedError('Must be implemented in subclass')

    def _initialize_min_max_rpm(self):
        """Initialize self.max_rpm and self.min_nonzero_rpm by modbus."""
        raise NotImplementedError('Must be implemented in subclass')

    def _set_rpm(self, rpm_setting):
        """Set fan speed to the given RPM.
        :param rpm_setting: The user supplied rpm setting.
        returns: The modbus write result."""
        raise NotImplementedError('Must be implemented in subclass')

    def _check_fan_speed_setting(self, speed_rpm):
        """Ensure that the caller's speed_rpm setting is valid.
        :param speed_rpm: The speed_rpm setting from the caller.
        :raises: SynseException on failure."""
        if self.hardware_type == 'emulator':
            if speed_rpm < 0:
                raise SynseException(
                    'Invalid speed setting {} for fan control.'.format(speed_rpm))
        elif self.hardware_type == 'production':
            if speed_rpm != 0:
                if not self.min_nonzero_rpm <= speed_rpm <= self.max_rpm:
                    raise SynseException(
                        'Invalid speed setting {} for fan control - '
                        'must be zero or between {} and {}'.format(
                            speed_rpm, self.min_nonzero_rpm, self.max_rpm))
        else:
            raise SynseException('Unknown hardware type {}.', self.hardware_type)

    def _fan(self, command):
        """ Fan speed control command for a given board and device.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the fan response.
        """
        # get the command data out from the incoming command
        device_id = command.data[_s_.DEVICE_ID]
        fan_speed = int(command.data[_s_.FAN_SPEED])

        # FIXME: override because main_blueprint doesn't distinguish between
        # 'fan_speed' and 'vapor_fan'
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
            logger.error(
                'No response for fan control for command: {}'.format(command.data))
            raise SynseException('No fan control response returned from RS485.')

        except Exception:
            raise SynseException(
                'Error controlling fan controller (device id: {})'.format(
                    device_id)), None, sys.exc_info()[2]

    def _fan_control(self, action='status', speed_rpm=None):
        """ Internal method for fan control action.

        Args:
            action (str): the fan control action to take. valid actions include:
                'status', 'set_speed'
            speed_rpm (int): the fan speed (in RPM) to set. note that the speed will
                only be set if the action is 'set_speed'.
             fan_direction (string): forward or reverse.

        Returns:
            dict: the fan speed reading.
        """
        with self._lock:
            if self.hardware_type == 'emulator':
                if action == 'set_speed' and speed_rpm is not None:
                    self._check_fan_speed_setting(speed_rpm)

                    with ModbusClient(method=self.method, port=self.device_name,
                                      timeout=self.timeout) as client:
                        # write speed
                        # This code is not doing conversion from rpm to hz, but afraid to
                        # touch it. We will do the conversion on production hardware and
                        # leave the emulator code alone.
                        result = client.write_registers(
                            self._register_map['speed_rpm'],
                            [speed_rpm],
                            unit=self.unit)

                        if result is None:
                            raise SynseException(
                                'No response received for fan control.')
                        elif isinstance(result, ExceptionResponse):
                            raise SynseException('RS485 Exception: {}'.format(result))

                # in all cases, read out / compute the fan_speed from RS485
                with ModbusClient(method=self.method, port=self.device_name,
                                  timeout=self.timeout) as client:
                    # read speed
                    result = client.read_holding_registers(
                        self._register_map['speed_rpm'],
                        count=1,
                        unit=self.unit)

                    if result is None:
                        raise SynseException(
                            'No response received for fan control.')
                    elif isinstance(result, ExceptionResponse):
                        raise SynseException('RS485 Exception: {}'.format(result))

                    # create client and read registers, composing a reading to return
                    return {
                        const.UOM_VAPOR_FAN: result.registers[0],
                        const.UOM_DIRECTION: 'forward'
                    }

            elif self.hardware_type == 'production':
                # Production
                # Write speed.
                if action == 'set_speed' and speed_rpm is not None:
                    if self.from_background:
                        self._write_indirect(speed_rpm)
                        return {const.UOM_VAPOR_FAN: speed_rpm}

                    else:
                        speed_rpm = int(speed_rpm)
                        self._check_fan_speed_setting(speed_rpm)
                        self._set_rpm(speed_rpm)
                        # Return the speed_rpm setting and not a read since the fan
                        # is likely ramping up or coasting down to the set speed.
                        return {const.UOM_VAPOR_FAN: speed_rpm}

                # Read speed.
                if self.from_background:
                    rpm, direction = self._read_indirect()
                else:
                    rpm, direction = self._read_direct()

                return {
                    const.UOM_VAPOR_FAN: rpm,
                    const.UOM_DIRECTION: direction,
                }

            raise SynseException(FanController.HARDWARE_TYPE_UNKNOWN.format(
                self.hardware_type))

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

        if device_type_string not in [const.DEVICE_VAPOR_FAN, const.DEVICE_FAN_SPEED]:
            # this command is not for us
            raise SynseException(
                'Incorrect device type "{}" for fan.'.format(device_type_string))

        # FIXME: override because main_blueprint doesn't distinguish between
        # 'fan_speed' and 'vapor_fan'
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
            logger.error(
                'No response for fan control for command: {}'.format(command.data))
            raise SynseException('No fan control response returned from RS485.')

        except Exception:
            raise SynseException(
                'Error controlling fan controller (device id: {})'.format(
                    device_id)), None, sys.exc_info()[2]

    def _read_direct(self):
        """Direct read of the fan controller. This read hits the bus.
        :returns: A set of (rpm, direction). rpm is an int. direction is
        forward or reverse."""
        return self._get_rpm(), self._get_direction()

    # def _read_indirect(self):
    #     """Indirect read of the fan controller.
    #     :returns: A set of (rpm, direction). rpm is an int. direction is
    #     forward or reverse."""
    #     logger.debug('_read_indirect')
    #
    #     # If we are not the vec leader we need to redirect this call to the leader.
    #     # The Synse configuration is supposed to be the same for all vecs in the chamber.
    #     if not FanController.is_vec_leader():
    #         response = FanController.redirect_call_to_vec_leader(request.url)
    #         return response[const.UOM_VAPOR_FAN], response[const.UOM_DIRECTION]
    #
    #     data_file = self._get_bg_read_file(
    #         str(self.unit), '{0:04x}'.format(self.register_base))
    #     data = FanController.read_sensor_data_file(data_file)
    #     return (
    #         int(data[0]),  # rpm
    #         data[1]        # direction
    #     )
    #
    # def _write_indirect(self, speed_rpm):
    #     """Indirect write to set the speed on the fan controller.
    #     :param speed_rpm: The speed to set in rpm."""
    #     # If we are not the vec leader we need to redirect this call to the leader.
    #     # The Synse configuration is supposed to be the same for all vecs in the chamber.
    #     if not FanController.is_vec_leader():
    #         FanController.redirect_call_to_vec_leader(request.url)
    #         return
    #
    #     data_file = self._get_bg_write_file(
    #         str(self.unit), '{0:04x}'.format(self.register_base))
    #     logger.debug('data_file: {}, speed_rpm: {}'.format(data_file, speed_rpm))
    #     FanController.write_device_data_file(data_file, str(speed_rpm))
