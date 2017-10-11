#!/usr/bin/env python
""" Synse Test class to avoid hardcoded strings.

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


class _S(object):
    """String class to avoid hardcoded strings in tests.
    We will need a similar file for dev code."""

    AIRFLOW_MILLIMETERS_PER_SECOND = 'airflow_mm_s'
    BLINK_OFF = 'steady'
    BLINK_ON = 'blink'
    BLINK_STATE = 'blink_state'
    BOARD_ID = 'board_id'
    BOARDS = 'boards'
    CYCLE = 'cycle'
    DEVICE_ID = 'device_id'
    DEVICE_INFO = 'device_info'
    DEVICE_TYPE = 'device_type'
    DEVICE_TYPE_CURRENT = 'current'
    DEVICE_TYPE_FAN = 'fan'              # TODO: Pretty sure that this is wrong. Should be fan_speed. (552)
    DEVICE_TYPE_FAN_SPEED = 'fan_speed'
    DEVICE_TYPE_FREQUENCY = 'frequency'  # Device is not currently supported by Synse.
    DEVICE_TYPE_HUMIDITY = 'humidity'
    DEVICE_TYPE_LEAKAGE = 'leakage'
    DEVICE_TYPE_LED = 'led'
    DEVICE_TYPE_PERCENT_LOAD = 'percent_load'
    DEVICE_TYPE_POWER = 'power'
    DEVICE_TYPE_PRESSURE = 'pressure'
    DEVICE_TYPE_TEMPERATURE = 'temperature'
    DEVICE_TYPE_VOLTAGE = 'voltage'
    DEVICES = 'devices'

    # TODO: Ticket. Should probably read device rather than sensor. (553)
    ERROR_BAD_DATA_AT_DEVICE = 'Bad data at sensor.'
    # TODO: Ticket Inconsistencies here. (555)
    ERROR_DEVICE_DOES_NOT_SUPPORT_SETTING = 'Device does not support setting {}.'
    ERROR_DEVICE_TYPE_NOT_SUPPORTED = 'Device type {} is not yet supported.'
    ERROR_FAN_COMMAND_NOT_SUPPORTED = 'Fan command not supported on this device.'
    ERROR_FLASK_404 = 'The requested URL was not found on the server.  ' \
                      'If you entered the URL manually please check your spelling and try again.'
    ERROR_LED_COMMAND_NOT_SUPPORTED = 'LED command not supported on this device.'
    ERROR_INVALID_BLINK_LED = 'Invalid blink state specified for LED.'
    ERROR_INVALID_COLOR_LED = 'Invalid LED color specified. (LED Color must be between 0x000000 and 0xffffff.)'
    ERROR_INVALID_STATE_LED = 'Invalid LED state provided for LED control.'
    ERROR_NO_BOARD_ON_RACK = 'No board on rack {} with id {}.'
    ERROR_NO_BOARD_WITH_ID = 'No board with id {}.'
    ERROR_NO_DEVICE_WITH_ID = 'No device with id {}.'
    ERROR_NO_RACK_WITH_ID = 'No rack with id {}.'
    ERROR_NO_RACK_FOUND_WITH_ID = 'No rack found with id: {}'
    ERROR_POWER_COMMAND_NOT_SUPPORTED = 'Power command not supported on this device.'
    # TODO: Ticket. Should probably read device type rather than sensor type. (553)
    ERROR_WRONG_DEVICE_TYPE = 'Wrong sensor type. ' \
                              'Request to read {}, but this sensor reads {}.'
    ERROR_NO_REGISTERED_DEVICE_FOR_BOARD = 'Board ID ({:08x}) not associated with any registered devicebus handler.'

    LED_COLOR = 'led_color'
    LED_STATE = 'led_state'
    INPUT_POWER = 'input_power'
    IP_ADDRESSES = 'ip_addresses'
    HEALTH = 'health'
    HOSTNAMES = 'hostnames'
    HTTP_CODE = 'http_code'
    MESSAGE = 'message'
    OFF = 'off'
    OK = 'ok'
    ON = 'on'
    OVER_CURRENT = 'over_current'
    POWER_OK = 'power_ok'
    POWER_STATUS = 'power_status'
    PRESSURE_PA = 'pressure_pa'
    RACK_ID = 'rack_id'
    RACKS = 'racks'
    SNMP_EMULATOR_DOWN = 'Bad IPv4/UDP transport address snmp-emulator-synse-testdevice1-board1@11012: ' \
                         '[Errno -2] Name or service not known'
    SNMP_READ_TIMEOUT = 'Error Indication: No SNMP response received before timeout'
    SNMP_V2C = 'v2c'
    SNMP_VERSION = 'snmp_version'
    SPEED_RPM = 'speed_rpm'
    STATES = 'states'
    TEMPERATURE_C = 'temperature_c'

    URI_FAN = '/fan'
    URI_LED = '/led'
    URI_POWER = '/power'
    URI_READ = '/read'
    URI_SCAN = '/scan'
    URI_SCAN_FORCE = '/scan/force'
    URI_VERSION = '/version'
