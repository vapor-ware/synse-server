#!/usr/bin/env python
""" Synse GS3-2010 Fan Control RS485 Device.

    Author: Andrew Cencini
    Date:   10/13/2016

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

from synse.devicebus.devices.rs485.fan_controller import FanController
from synse.protocols.modbus import modbus_common  # nopep8

logger = logging.getLogger(__name__)


class GS32010Fan(FanController):
    """ Device subclass for GS3-2010 fan controller using RS485 communications.
    """
    _instance_name = 'gs3-2010'

    def __init__(self, **kwargs):
        super(GS32010Fan, self).__init__(**kwargs)

        logger.debug('GS32010Fan kwargs: {}'.format(kwargs))

        # the register base is used to map multiple device instances to a device-specific
        # base address such that each device has its own map of registers
        self.register_base = int(kwargs['base_address'], 16)

        # Map of registers for fan control. Only used by the emulator.
        if self.hardware_type == 'emulator':
            self._register_map = {
                'speed_rpm': self.register_base + 0x0000
            }

        logger.debug('GS32010Fan self: {}'.format(dir(self)))

    def _get_direction(self):
        """Production only direction reads from gs3_2010_fan (vapor_fan).
        :returns: String forward or reverse."""
        client = self.create_modbus_client()
        return modbus_common.get_fan_direction_gs3(
            client.serial_device, self.slave_address)

    def _get_rpm(self):
        """Production only rpm reads from gs3_2010_fan (vapor_fan).
        :returns: Integer rpm."""
        client = self.create_modbus_client()
        return modbus_common.get_fan_rpm_gs3(
            client.serial_device, self.slave_address)

    def _initialize_min_max_rpm(self):
        """Initialize self.max_rpm and self.min_nonzero_rpm by modbus."""
        client = self.create_modbus_client()
        # Maximum rpm supported by the fan motor.
        self.max_rpm = modbus_common.get_fan_max_rpm_gs3(
            client.serial_device, self.slave_address)
        # Minimum rpm setting allowed. For now this is 10% of the max. This is
        # due to minimal back EMF at low rpms.
        self.min_nonzero_rpm = self.max_rpm / 10

    def _set_rpm(self, rpm_setting):
        """Set fan speed to the given RPM.
        :param rpm_setting: The user supplied rpm setting.
        returns: The modbus write result."""
        client = self.create_modbus_client()
        return modbus_common.set_fan_rpm_gs3(
            client.serial_device, self.slave_address,
            rpm_setting, self.max_rpm)
