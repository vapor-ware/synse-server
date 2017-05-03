#!/usr/bin/env python
""" String constants used throughout OpenDCRE.

    Author: Erick Daniszewski
    Date:   18 April 2017

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

RACK_ID = intern('rack_id')
BOARD_ID = intern('board_id')
DEVICE_ID = intern('device_id')
DEVICE_TYPE = intern('device_type')
DEVICE_TYPE_STRING = intern('device_type_string')
DEVICE_NAME = intern('device_name')
FORCE = intern('force')

# LOCATION
PHYSICAL_LOC = intern('physical_location')
CHASSIS_LOC = intern('chassis_location')
LOC_UNKNOWN = intern('unknown')
LOC_VERTICAL = intern('vertical')
LOC_HORIZONTAL = intern('horizontal')
LOC_DEPTH = intern('depth')


# POWER
POWER_ACTION = intern('power_action')
PWR_ON = intern('on')
PWR_OFF = intern('off')
PWR_CYCLE = intern('cycle')
PWR_STATUS = intern('status')


# BOOT TARGET
BOOT_TARGET = intern('boot_target')
BT_NO_OVERRIDE = intern('no_override')
BT_PXE = intern('pxe')
BT_HDD = intern('hdd')


# LED
LED_STATE = intern('led_state')
LED_COLOR = intern('led_color')
LED_BLINK_STATE = intern('blink_state')
LED_ON = intern('on')
LED_OFF = intern('off')
LED_NO_OVERRIDE = intern('no_override')
LED_BLINK = intern('blink')
LED_STEADY = intern('steady')


# FAN
FAN_SPEED = intern('fan_speed')


# ERRORS
ERR_BOARD_ID_NOT_REGISTERED = 'Board ID ({}) not registered with any known device bus.'
