#!/usr/bin/env python
""" Constant values used throughout Synse.

    Author: Erick Daniszewski
    Date:   09/21/2016

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

# ---------------------------------------------------------
# Endpoint definitions, defined for the convenience of
# url building
# ---------------------------------------------------------
endpoint_prefix = '/synse/'
port = 5000


# ---------------------------------------------------------
# Device interface board id ranges. The ranges specified
# here are inclusive, where the 0th element is the lower
# bound and the 1st element is the upper bound.
# ---------------------------------------------------------
PLC_BOARD_RANGE = (0x00000000, 0x3fffffff)
IPMI_BOARD_RANGE = (0x40000000, 0x4fffffff)
RS485_BOARD_RANGE = (0x50000000, 0x5000ffff)
I2C_BOARD_RANGE = (0x50010000, 0x5001ffff)
SNMP_BOARD_RANGE = (0x60000000, 0x6fffffff)
REDFISH_BOARD_RANGE = (0x70000000, 0x7fffffff)


# ---------------------------------------------------------
# Board type enum returned by get_board_type().
# ---------------------------------------------------------
BOARD_TYPE_UNKNOWN = 0
BOARD_TYPE_PLC = 1
BOARD_TYPE_IPMI = 2
BOARD_TYPE_RS485 = 3
BOARD_TYPE_I2C = 4
BOARD_TYPE_SNMP = 5
BOARD_TYPE_REDFISH = 6


def get_board_type(board_id):
    """ Given the board id, what type of board is it?

    Args:
        board_id (int | str): The board id.

    Returns:
        int: the internal board type number.
    """

    # Convert board_id from string to int if needed.
    if isinstance(board_id, basestring):
        board_id = int(board_id, 16)

    # Return the board type.
    if PLC_BOARD_RANGE[0] <= board_id <= PLC_BOARD_RANGE[1]:
        return BOARD_TYPE_PLC

    if IPMI_BOARD_RANGE[0] <= board_id <= IPMI_BOARD_RANGE[1]:
        return BOARD_TYPE_IPMI

    if RS485_BOARD_RANGE[0] <= board_id <= RS485_BOARD_RANGE[1]:
        return BOARD_TYPE_RS485

    if SNMP_BOARD_RANGE[0] <= board_id <= SNMP_BOARD_RANGE[1]:
        return BOARD_TYPE_SNMP

    if REDFISH_BOARD_RANGE[0] <= board_id <= REDFISH_BOARD_RANGE[1]:
        return BOARD_TYPE_REDFISH

    if I2C_BOARD_RANGE[0] <= board_id <= I2C_BOARD_RANGE[1]:
        return BOARD_TYPE_I2C

    return BOARD_TYPE_UNKNOWN

# ---------------------------------------------------------
# Devicebus hardware specification
# ---------------------------------------------------------
DEVICEBUS_VEC_V1 = 0x10
DEVICEBUS_EMULATOR_V1 = 0x20
DEVICEBUS_UNKNOWN_HARDWARE = 0xFF


# ---------------------------------------------------------
# Device name constants
# ---------------------------------------------------------
DEVICE_AIRFLOW = intern('airflow')
DEVICE_CURRENT = intern('current')
DEVICE_FAN_SPEED = intern('fan_speed')
DEVICE_HUMIDITY = intern('humidity')
DEVICE_LED = intern('led')
DEVICE_POWER = intern('power')
DEVICE_POWER_SUPPLY = intern('power_supply')
DEVICE_PRESSURE = intern('pressure')
DEVICE_SYSTEM = intern('system')
DEVICE_TEMPERATURE = intern('temperature')
DEVICE_THERMISTOR = intern('thermistor')
DEVICE_VAPOR_BATTERY = intern('vapor_battery')
DEVICE_VAPOR_FAN = intern('vapor_fan')
DEVICE_VAPOR_LED = intern('vapor_led')
DEVICE_VAPOR_RECTIFIER = intern('vapor_rectifier')
DEVICE_VOLTAGE = intern('voltage')
DEVICE_NONE = intern('none')  # Same as unknown.


# ---------------------------------------------------------
# Device unit of measure constants
# ---------------------------------------------------------
UOM_AIRFLOW = intern('airflow_mm_s')
UOM_FAN_SPEED = intern('speed_rpm')
UOM_HUMIDITY = intern('humidity')
UOM_PRESSURE = intern('pressure_kpa')
UOM_TEMPERATURE = intern('temperature_c')
UOM_THERMISTOR = intern('temperature_c')
UOM_VAPOR_FAN = intern('speed_rpm')
UOM_VOLTAGE = intern('voltage')


# ---------------------------------------------------------
# Mapping of device names to unit of measure for the device
# ---------------------------------------------------------
uom_map = {
    DEVICE_AIRFLOW: UOM_AIRFLOW,
    DEVICE_CURRENT: None,
    DEVICE_FAN_SPEED: UOM_FAN_SPEED,
    DEVICE_HUMIDITY: None,
    DEVICE_LED: None,
    DEVICE_POWER: None,
    DEVICE_POWER_SUPPLY: None,
    DEVICE_PRESSURE: UOM_PRESSURE,
    DEVICE_SYSTEM: None,
    DEVICE_TEMPERATURE: UOM_TEMPERATURE,
    DEVICE_THERMISTOR: UOM_THERMISTOR,
    DEVICE_VAPOR_BATTERY: None,
    DEVICE_VAPOR_FAN: UOM_VAPOR_FAN,
    DEVICE_VAPOR_LED: None,
    DEVICE_VAPOR_RECTIFIER: None,
    DEVICE_VOLTAGE: UOM_VOLTAGE,
    DEVICE_NONE: None,
}


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
