#!/usr/bin/env python
""" Constant values used throughout OpenDCRE.

    Author: Erick Daniszewski
    Date:   09/21/2016

    \\//
     \/apor IO

-------------------------------
Copyright (C) 2015-17  Vapor IO

This file is part of OpenDCRE.

OpenDCRE is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

OpenDCRE is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenDCRE.  If not, see <http://www.gnu.org/licenses/>.
"""

# ---------------------------------------------------------
# Endpoint definitions, defined for the convenience of
# url building
# ---------------------------------------------------------
endpoint_prefix = '/opendcre/'
port = 5000


# ---------------------------------------------------------
# Device interface board id ranges. The ranges specified
# here are inclusive, where the 0th element is the lower
# bound and the 1st element is the upper bound.
# ---------------------------------------------------------
PLC_BOARD_RANGE = (0x00000000, 0x3fffffff)
IPMI_BOARD_RANGE = (0x40000000, 0x4fffffff)
REDFISH_BOARD_RANGE = (0x70000000, 0x7fffffff)


# ---------------------------------------------------------
# Board type enum returned by get_board_type().
# ---------------------------------------------------------
BOARD_TYPE_UNKNOWN = 0
BOARD_TYPE_PLC = 1
BOARD_TYPE_IPMI = 2
BOARD_TYPE_REDFISH = 5


def get_board_type(board_id):
    """Given the board id, what type of board is it?
    :param board_id: The board id."""

    # Convert board_id from string to int if needed.
    if isinstance(board_id, basestring):
        board_id = int(board_id, 16)

    # Return the board type.
    if PLC_BOARD_RANGE[0] <= board_id <= PLC_BOARD_RANGE[1]:
        return BOARD_TYPE_PLC

    if IPMI_BOARD_RANGE[0] <= board_id <= IPMI_BOARD_RANGE[1]:
        return BOARD_TYPE_IPMI

    if REDFISH_BOARD_RANGE[0] <= board_id <= REDFISH_BOARD_RANGE[1]:
        return BOARD_TYPE_REDFISH

    return BOARD_TYPE_UNKNOWN

# ---------------------------------------------------------
# Devicebus hardware specification
# ---------------------------------------------------------
DEVICEBUS_RPI_HAT_V1 = 0x00
DEVICEBUS_VEC_V1 = 0x10
DEVICEBUS_EMULATOR_V1 = 0x20
DEVICEBUS_UNKNOWN_HARDWARE = 0xFF


# ---------------------------------------------------------
# Device name constants
# ---------------------------------------------------------
DEVICE_VAPOR_LED = 'vapor_led'
DEVICE_LED = 'led'
DEVICE_SYSTEM = 'system'
DEVICE_POWER = 'power'
DEVICE_VAPOR_RECTIFIER = 'vapor_rectifier'
DEVICE_VAPOR_BATTERY = 'vapor_battery'
DEVICE_HUMIDITY = 'humidity'
DEVICE_FAN_SPEED = 'fan_speed'
DEVICE_VAPOR_FAN = 'vapor_fan'
DEVICE_CURRENT = 'current'
DEVICE_TEMPERATURE = 'temperature'
DEVICE_THERMISTOR = 'thermistor'
DEVICE_PRESSURE = 'pressure'
DEVICE_NONE = 'none'  # Same as unknown.
DEVICE_POWER_SUPPLY = 'power_supply'
DEVICE_AIRFLOW = 'airflow'
DEVICE_VOLTAGE = 'voltage'


# ---------------------------------------------------------
# Mappings between device type names and bus codes
# ---------------------------------------------------------
device_name_codes = {
    DEVICE_VAPOR_LED:        0x08,
    DEVICE_LED:              0x10,
    DEVICE_SYSTEM:           0x12,  # actually "ipmb" but represent as "system"
    DEVICE_POWER:            0x40,
    DEVICE_VAPOR_RECTIFIER:  0x48,
    DEVICE_VAPOR_BATTERY:    0x4A,  # placeholder value
    DEVICE_HUMIDITY:         0x4E,
    DEVICE_FAN_SPEED:        0x82,
    DEVICE_VAPOR_FAN:        0x88,
    DEVICE_CURRENT:          0x90,
    DEVICE_TEMPERATURE:      0x9A,
    DEVICE_THERMISTOR:       0x9C,
    DEVICE_PRESSURE:         0xEE,
    DEVICE_POWER_SUPPLY:     0xF0,  # placeholder value
    DEVICE_AIRFLOW:          0xF2,  # placeholder value
    DEVICE_NONE:             0xFF
}
