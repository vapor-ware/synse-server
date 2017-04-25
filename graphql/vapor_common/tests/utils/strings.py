#!/usr/bin/env python
""" OpenDCRE Test class to avoid hardcoded strings.

    \\//
     \/apor IO
"""


class _S(object):
    """String class to avoid hardcoded strings in tests.
    We will need a similar file for dev code."""

    BLINK_OFF = 'steady'
    BLINK_ON = 'blink'
    BLINK_STATE = 'blink_state'
    BOARD_ID = 'board_id'
    BOARDS = 'boards'
    CYCLE = 'cycle'
    DEVICE_ID = 'device_id'
    DEVICE_INFO = 'device_info'
    DEVICE_TYPE = 'device_type'
    DEVICE_TYPE_FAN = 'fan'              # TODO: Pretty sure that this is wrong. Should be fan_speed. (552)
    DEVICE_TYPE_FAN_SPEED = 'fan_speed'
    DEVICE_TYPE_FREQUENCY = 'frequency'  # Device is not currently supported by OpenDCRE.
    DEVICE_TYPE_HUMIDITY = 'humidity'    # Device is not currently supported by OpenDCRE AFAIK.
    DEVICE_TYPE_LEAKAGE = 'leakage'
    DEVICE_TYPE_LED = 'led'
    DEVICE_TYPE_POWER = 'power'
    DEVICE_TYPE_PRESSURE = 'pressure'    # Device is not currently supported by OpenDCRE AFAIK.
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
    RACK_ID = 'rack_id'
    RACKS = 'racks'
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
