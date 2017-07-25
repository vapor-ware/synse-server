#!/usr/bin/env python
""" Synse IPMI Bridge.

Uses OpenStack's pyghmi as back-end IPMI library.
see: https://github.com/openstack/pyghmi

    Author:  andrew
    Date:    6/16/2016

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

from pyghmi import constants

from synse.definitions import BMC_PORT
from synse.devicebus.devices.ipmi.vapor_ipmi_common import IpmiCommand
from synse.devicebus.devices.ipmi.vapor_ipmi_oem_flex import \
    get_flex_victoria_power_reading
from synse.errors import SynseException

logger = logging.getLogger(__name__)


def power(username=None, password=None, ip_address=None, port=BMC_PORT, cmd=None,
          reading_method=None):
    """ Get/set power status for remote host.

    Args:
        username (str): username to connect to BMC with.
        password (str): password to connect to BMC with.
        ip_address (str): BMC IP address.
        port (int): BMC port.
        cmd (str): 'on', 'off', 'cycle', 'status'
        reading_method (str): designation for routing power consumption readings.
            If 'flex-victoria', then the Flex OEM reading method is used.
            If 'None', then no power reading is used.
            If 'dcmi', then DCMI power reading is used.

    Returns:
        dict: power status after command execution, or raises IpmiException or
            InvalidParameterValue from pyghmi
    """
    # power cycle is hard reset in ipmi/pyghmi
    response = dict()
    with IpmiCommand(ip_address=ip_address, username=username, password=password,
                     port=port) as ipmicmd:
        if cmd == 'status':
            result = ipmicmd.get_power()
            response['power_status'] = result['powerstate']
        elif cmd == 'cycle':
            result = ipmicmd.get_power()
            # only power cycle if the machine is on
            if result['powerstate'] == 'on':
                ipmicmd.set_power('off', wait=15)
                result = ipmicmd.set_power('on', wait=True)
            response['power_status'] = result['powerstate']
        else:
            result = ipmicmd.set_power(cmd, wait=15)
            response['power_status'] = result['powerstate']
        if 'error' in result:
            raise SynseException('Error executing IPMI power command on {} : {}'.format(
                ip_address, result['error']))
        try:
            # first get additional information about the power health
            chassis_status = _get_chassis_status(username, password, ip_address)
            response['over_current'] = chassis_status.get('power_overload', 'unknown')
            # FIXME (etd): for the below, if there is no 'power_fault', we are evaluating
            # "not 'unknown'" which will be False -- is this expected/desired?
            # invert 'fault' for 'ok'
            response['power_ok'] = not chassis_status.get('power_fault', 'unknown')
        except Exception as e:
            response['over_current'] = 'unknown'
            response['power_ok'] = 'unknown'
            logger.error('Error getting chassis status on power command for {} : {}'.format(
                ip_address, e.message))

        try:
            # next, attempt to get input power reading, and if unavailable, set the response
            # to 'unknown'
            response['input_power'] = 'unknown'
            if reading_method is not None:
                if reading_method == 'flex-victoria':
                    response['input_power'] = get_flex_victoria_power_reading(
                        username, password, ip_address)['input_power']
                elif reading_method == 'dcmi':
                    response['input_power'] = _get_power_reading(username, password,
                                                                 ip_address)['input_power']
        except Exception as e:
            response['input_power'] = 'unknown'
            logger.error('Error getting power reading on power command for {} : {}'.format(
                ip_address, e.message))

        return response


def sensors(username=None, password=None, ip_address=None, port=BMC_PORT):
    """ Get a list of sensors from remote system.

    Args:
        username (str): the username to use to connect to the remote BMC.
        password (str): the password to use to connect to the remote BMC.
        ip_address (str): the IP address of the BMC.
        port (int): BMC port.

    Returns:
        list[dict]: sensor number, id string, and type for each sensor available.
    """
    with IpmiCommand(ip_address=ip_address, username=username, password=password,
                     port=port) as ipmicmd:
        sdr = ipmicmd.init_sdr()
        if sdr is None:
            raise SynseException('Error initializing SDR from IPMI BMC {}'.format(ip_address))
        response = [
            {
                'sensor_number': sensor.sensor_number,
                'id_string': sensor.name,
                'sensor_type': sensor.sensor_type
            } for sensor in sdr.sensors.values()]
        return response


def _convert_health_to_string(health):
    """ Convert a numeric health value to string.

    Args:
        health (int): the numeric value to convert.

    Returns:
        str: the string value of the converted health indicator. returns
            string version of the heath numeric value if it does not match
            what pyghmi has defined. (NB: it may be the case that health
            indicators stack as they may be ORed into a single value by
            pyghmi, so logic may need tweaking).
    """
    if health == constants.Health.Ok:
        return 'ok'
    elif health == constants.Health.Warning:
        return 'warning'
    elif health == constants.Health.Critical:
        return 'critical'
    elif health == constants.Health.Failed:
        return 'failed'

    return str(health)


def read_sensor(sensor_name, username=None, password=None, ip_address=None, port=BMC_PORT):
    """ Get a converted sensor reading back from the remote system for a
    given sensor_name.

    Args:
        username (str): username to connect to BMC with.
        password (str): password to connect to BMC with.
        ip_address (str): BMC IP address.
        port (int): BMC port.
        sensor_name (str): the id_string of the sensor to read.
            (NB ABC: this is a vestige of pyghmi, it would be
            better to read by sensor number)

    Returns:
        dict: the converted sensor reading for the given sensor_name.

    Raises:
        IpmiException: if the the sensor is not available (e.g. the
            power is off).
        ValueError: invalid sensor name was specified.
    """
    if sensor_name is not None:
        result = dict()
        with IpmiCommand(ip_address=ip_address, username=username, password=password,
                         port=port) as ipmicmd:
            reading = ipmicmd.get_sensor_reading(sensor_name)
            result['sensor_reading'] = reading.value
            result['health'] = _convert_health_to_string(reading.health)
            result['states'] = reading.states
            return result

    raise ValueError('Must specify a sensor name when retrieving sensor reading via IPMI.')


def get_boot(username=None, password=None, ip_address=None, port=BMC_PORT):
    """ Get boot target from remote host.

    Args:
        username (str): username to connect to BMC with.
        password (str): password to connect to BMC with.
        ip_address (str): BMC IP address.
        port (int): BMC port.

    Returns:
        dict: boot target as observed, or IpmiException from pyghmi.
    """
    response = dict()
    with IpmiCommand(ip_address=ip_address, username=username, password=password,
                     port=port) as ipmicmd:
        result = ipmicmd.get_bootdev()
        if 'error' in result:
            raise SynseException(
                'Error retrieving boot device from IPMI BMC {} : {}'.format(
                    ip_address, result['error'])
            )

        # FIXME (etd) - here, if bootdev doesn't exist, we use 'unknown'. in the dict `get`
        # in the following line, there is no record for unknown, so it will default to the
        # value of `None` -- is this desired?
        bootdev = result.get('bootdev', 'unknown')
        bootdev = dict(network='pxe', hd='hdd', default='no_override').get(bootdev)
        response['target'] = bootdev
        return response


def set_boot(username=None, password=None, ip_address=None, port=BMC_PORT, target=None):
    """ Set the boot target on remote host.

    Args:
        username (str): username to connect to BMC with.
        password (str): password to connect to BMC with.
        ip_address (str): BMC IP address.
        port (int): BMC port.
        target (str): the boot target to set the remote host to.

    Returns:
        dict: boot target as observed, or IpmiException from pyghmi.
    """
    response = dict()
    with IpmiCommand(ip_address=ip_address, username=username, password=password,
                     port=port) as ipmicmd:
        target = dict(pxe='network', hdd='hd', no_override='default').get(target)
        result = ipmicmd.set_bootdev(bootdev=target)
        if 'error' in result:
            raise SynseException(
                'Error setting boot device from IPMI BMC {} : {}'.format(
                    ip_address, result['error'])
            )

        # FIXME (etd) - here, if bootdev doesn't exist, we use 'unknown'. in the dict `get`
        # in the following line, there is no record for unknown, so it will default to the
        # value of `None` -- is this desired?
        bootdev = result.get('bootdev', 'unknown')
        bootdev = dict(network='pxe', hd='hdd', default='no_override').get(bootdev)
        response['target'] = bootdev
        return response


def get_inventory(username=None, password=None, ip_address=None, port=BMC_PORT):
    """ Get inventory information from the FRU of the remote system.

    Args:
        username (str): the username to connect to BMC with.
        password (str): the password to connect to BMC with.
        ip_address (str): the IP address of the BMC.
        port (int): BMC port.

    Returns:
        dict: inventory information from the remote system.
    """
    response = dict()
    with IpmiCommand(ip_address=ip_address, username=username, password=password,
                     port=port) as ipmicmd:
        result = ipmicmd.get_inventory_of_component('System')
        if 'error' in result:
            raise SynseException(
                'Error retrieving System inventory from IPMI BMC {} : {}'.format(
                    ip_address, result['error'])
            )

        response['chassis_info'] = dict()
        response['chassis_info']['chassis_type'] = result.get('Chassis type', '')
        response['chassis_info']['part_number'] = result.get('Chassis part number', '')
        response['chassis_info']['serial_number'] = result.get('Chassis serial number', '')
        response['board_info'] = dict()
        response['board_info']['manufacturer'] = result.get('Board manufacturer', '')
        response['board_info']['part_number'] = result.get('Board part number', '')
        response['board_info']['product_name'] = result.get('Board product name', '')
        response['board_info']['serial_number'] = result.get('Board serial number', '')
        response['product_info'] = dict()
        response['product_info']['asset_tag'] = result.get('Asset Number', '')
        response['product_info']['part_number'] = result.get('Model', '')
        response['product_info']['manufacturer'] = result.get('Manufacturer', '')
        response['product_info']['product_name'] = result.get('Product name', '')
        response['product_info']['serial_number'] = result.get('Serial Number', '')
        response['product_info']['version'] = result.get('Hardware Version', '')
        return response


def _get_temperature_readings(username=None, password=None, ip_address=None, port=BMC_PORT,
                              entity=None):
    """ Internal wrapper for 'Get Temperature Reading' DCMI command.

    Args:
        username (str): the username to connect to BMC with.
        password (str): the password to connect to BMC with.
        ip_address (str): the IP address of the BMC to connect to.
        port (int): BMC port.
        entity (str): the entity to get temperature readings for:
            'inlet', 'cpu', or 'system_board'.

    Returns:
        dict: a dictionary of 'readings' containing a list of readings
            retrieved for the given entity type. These readings include
            entity and instance IDs for use elsewhere, in addition to a
            temperature_c reading.
    """
    with IpmiCommand(ip_address=ip_address, username=username, password=password,
                     port=port) as ipmicmd:
        cmd_data = [0xdc, 0x01]
        if entity == 'inlet':
            cmd_data.append(0x40)  # entity ID (air inlet)
            cmd_data.append(0x00)  # instance ID (0x00 means return all instances)
            cmd_data.append(0x01)  # starting instance ID (0x01 means start with the first)
        elif entity == 'cpu':
            cmd_data.append(0x41)
            cmd_data.append(0x00)
            cmd_data.append(0x01)
        elif entity == 'system_board':
            cmd_data.append(0x41)
            cmd_data.append(0x00)
            cmd_data.append(0x01)
        else:
            raise ValueError('Invalid DCMI entity type specified for temperature reading command.')

        result = ipmicmd.raw_command(netfn=0x2c, command=0x10, data=tuple(cmd_data))
        if 'error' in result:
            raise SynseException(
                'Error executing DCMI temperature readings command on {} : {}'.format(
                    ip_address, result['error'])
            )

        readings = {'readings': []}

        # TODO: read byte 1 instead which has the actual total number of responses, as opposed to
        # byte 2 which has the total in the response for a single command (no more than 8). This
        # means we will iterate via the starting instance id through all of the possible instances
        # until none remain.

        start_byte = 3  # start on first byte of reading
        for _ in range(0, result['data'][2]):
            # get the reading from the lower 7 bits
            temperature = float(result['data'][start_byte] & 0b01111111)
            # if the upper bit is a 1, the sign is negative
            if result['data'][start_byte] >> 7 & 0b01 == 0b01:
                temperature *= -1.0
            instance = result['data'][start_byte + 1]
            start_byte += 2
            readings['readings'].append([
                {'temperature_c': temperature, 'entity': entity, 'instance': instance}
            ])
        return readings


def _get_power_reading(username=None, password=None, ip_address=None, port=BMC_PORT):
    """ Internal wrapper for the 'Get Power Reading' DCMI command.

    Args:
        username (str): the username to connect to BMC with.
        password (str): the password to connect to BMC with.
        ip_address (str): the IP address of the BMC.
        port (int): BMC port.

    Returns:
        dict: power reading information from the remote system.

    Raises:
        SynseException: in cases where power reading is not active.
    """
    with IpmiCommand(ip_address=ip_address, username=username, password=password,
                     port=port) as ipmicmd:
        result = ipmicmd.raw_command(netfn=0x2c, command=0x02, data=(0xdc, 0x01, 0x00, 0x00))
        if 'error' in result:
            raise SynseException(
                'Error executing DCMI power reading command on {} : {}'.format(
                    ip_address, result['error'])
            )

        # if power measurement is inactive, we may be giving back back data.
        if (result['data'][17] >> 6) & 0x01 == 0x00:
            raise SynseException('Error reading DCMI power - power measurement is not active.')

        return {'input_power': float(result['data'][1] | (result['data'][2] << 8))}


def _get_chassis_status(username=None, password=None, ip_address=None, port=BMC_PORT):
    """ Internal wrapper for the 'Get Chassis Status' IPMI command.

    Args:
        username (str): the username to connect to BMC with.
        password (str): the password to connect to BMC with.
        ip_address (str): the IP address of the BMC.
        port (int): BMC port.

    Returns:
        dict: chassis status information from the remote system.
    """
    response = dict()
    with IpmiCommand(ip_address=ip_address, username=username, password=password,
                     port=port) as ipmicmd:
        result = ipmicmd.raw_command(netfn=0, command=1, data=[])
        if 'error' in result:
            raise SynseException(
                'Error executing chassis status command on {} : {}'.format(
                    ip_address, result['error'])
            )

        if result['command'] != 1 or result['netfn'] != 1 or result['code'] != 0:
            raise SynseException(
                'Error receiving chassis status response on {} : rc {}'.format(
                    ip_address, hex(result['code]']))
            )

        # process result and stick into fields of response
        # first: power restore policy
        response['power_restore_policy'] = 'unknown'
        if (result['data'][0] >> 6) & 0b11 == 0b00:
            response['power_restore_policy'] = 'power_off'
        elif (result['data'][0] >> 6) & 0b11 == 0b01:
            response['power_restore_policy'] = 'previous_state'
        elif (result['data'][0] >> 6) & 0b11 == 0b10:
            response['power_restore_policy'] = 'power_on'

        # next, power control fault
        response['power_control_fault'] = False if (result['data'][0] >> 4 & 0b1) == 0b00 else True

        # then power fault
        response['power_fault'] = False if (result['data'][0] >> 3 & 0b1) == 0b00 else True

        # then interlock
        response['interlock_active'] = False if (result['data'][0] >> 2 & 0b1) == 0b00 else True

        # overload
        response['power_overload'] = False if (result['data'][0] >> 1 & 0b1) == 0b00 else True

        # power on?
        response['power_status'] = 'off' if result['data'][0] & 0b1 == 0b00 else 'on'

        # last power event
        response['last_power_event'] = 'unknown'
        if (result['data'][1] >> 4) & 0b01 == 0b01:
            response['last_power_event'] = 'power_on_by_ipmi'
        elif (result['data'][1] >> 3) & 0b01 == 0b01:
            response['last_power_event'] = 'power_down_by_power_fault'
        elif (result['data'][1] >> 2) & 0b01 == 0b01:
            response['last_power_event'] = 'power_down_by_interlock'
        elif (result['data'][1] >> 1) & 0b01 == 0b01:
            response['last_power_event'] = 'power_down_by_overload'
        elif result['data'][1] & 0b01 == 0b01:
            response['last_power_event'] = 'ac_failed'

        # led command supported
        response['chassis_identify_supported'] = True if (result['data'][2] >> 6 & 0b1) == 0b01 \
            else 'unspecified'

        # led state
        if (result['data'][2] >> 5) & 0x01 or (result['data'][2] >> 4) & 0x01:
            response['led_state'] = 'on'
        else:
            response['led_state'] = 'off'

        # fan fault
        response['fan_fault'] = (result['data'][2] >> 3 & 0b1) == 0b01

        # drive fault
        response['drive_fault'] = (result['data'][2] >> 2 & 0b1) == 0b01

        # lockout active
        response['lockout_active'] = (result['data'][2] >> 1 & 0b1) == 0b01

        # chassis intrusion active
        response['chassis_intrusion'] = (result['data'][2] & 0b1) == 0b01

    return response


def get_identify(username=None, password=None, ip_address=None, port=BMC_PORT):
    """ Retrieve remote system LED status.

    Args:
        username (str): username to connect to BMC.
        password (str): password to connect to BMC.
        ip_address (str): BMC IP address.
        port (int): BMC port.

    Returns:
        dict: LED status as reported by remote system.
    """
    return {'led_state': _get_chassis_status(username, password, ip_address, port=port).get(
        'led_state', 'unknown')}


def set_identify(username=None, password=None, ip_address=None, port=BMC_PORT, led_state=None):
    """ Turn the remote system LED on or off.

    Args:
        username (str): username to connect to BMC with.
        password (str): password to connect to BMC with.
        ip_address (str): BMC IP address.
        port (int): BMC port.
        led_state (int): 1 == Force on, 0 == Force off.

    Returns:
        dict: LED state as set.
    """
    # Force on if True, Force off if False (indefinite duration)
    state = led_state == 1
    with IpmiCommand(ip_address=ip_address, username=username, password=password,
                     port=port) as ipmicmd:
        ipmicmd.set_identify(on=state)
        return {'led_state': led_state}


def get_dcmi_capabilities(username=None, password=None, ip_address=None, port=BMC_PORT,
                          parameter_selector=None):
    """ Get DCMI capabilities from the remote BMC.

    Args:
        username (str): username to connect to BMC with.
        password (str): password to connect to BMC with.
        ip_address (str): BMC IP address.
        port (int): BMC port.
        parameter_selector (int): the ID of the parameter to retrieve.

    Returns:
        dict: the formatted DCMI capabilities.

    Raises:
        SynseException: IPMI command failed or provided invalid response.
    """
    if parameter_selector is None or (parameter_selector < 1 or parameter_selector > 5):
        raise ValueError('Invalid parameter selector provided to get_dcmi_capabilities.')

    with IpmiCommand(ip_address=ip_address, username=username, password=password,
                     port=port) as ipmicmd:
        result = ipmicmd.raw_command(netfn=0x2c, command=0x01, data=(0xdc, parameter_selector))
        if 'error' in result:
            raise SynseException(
                'Error executing get DCMI capabilities command on {} : {}'.format(
                    ip_address, result['error'])
            )

        # byte 0 should always be 0xdc
        if result['data'][0] != 0xdc:
            raise SynseException(
                'Error in response to get DCMI capabilities command on {}: Invalid '
                'first byte.'.format(ip_address)
            )

        # to know power reading command is truly supported, we require DCMI 1.5
        if result['data'][1] != 0x01 or result['data'][2] != 0x05:
            raise SynseException('DCMI Version 1.5 is required for support by Synse.')

        # byte 3 must be 0x02 in DCMI 1.5
        if result['data'][3] != 0x02:
            raise SynseException(
                'Error in response to get DCMI capabilities command on {}: Parameter '
                'revision must be 0x02.'.format(ip_address)
            )

        response = dict()

        if parameter_selector == 0x01:
            # byte 1 is reserved
            response['power_management'] = bool(result['data'][5] & 0x01)
            response['secondary_lan_available'] = bool((result['data'][6] >> 2) & 0x01)
            response['serial_tmode_available'] = bool((result['data'][6] >> 1) & 0x01)
            response['in_band_channel_available'] = bool(result['data'][6] & 0x01)

        elif parameter_selector == 0x02:
            response['number_sel_entries'] = (result['data'][5] & 0b1111) << 8 | result['data'][6]
            response['record_flush_on_sel_rollover'] = bool((result['data'][6] >> 6) & 0x01)
            response['entire_sel_flush_on_sel_rollover'] = bool((result['data'][6] >> 7) & 0x01)
            response['sel_rollover_flush_enabled'] = bool((result['data'][6] >> 8) & 0x01)
            # bytes 7..8 reserved
            response['temp_monitoring_sample_freq_sec'] = result['data'][9]

        elif parameter_selector == 0x03:
            response['power_mgmt_device_address'] = result['data'][5]
            response['power_mgmt_channel_number'] = result['data'][6] >> 4
            response['power_mgmt_device_revision'] = result['data'][6] & 0x0f

        elif parameter_selector == 0x04:
            response['primary_lan_channel_number'] = result['data'][5]
            response['secondary_lan_channel_number'] = result['data'][6]
            response['serial_oob_channel_number'] = result['data'][7]

        elif parameter_selector == 0x05:
            response['num_supported_time_periods'] = result['data'][5]
            response['time_periods'] = list()
            for x in range(0, response['num_supported_time_periods']):
                duration_units = 'seconds'
                if (result['data'][6 + x] >> 6) & 0b01:
                    duration_units = 'minutes'
                elif (result['data'][6 + x] >> 6) & 0b10:
                    duration_units = 'hours'
                elif (result['data'][6 + x] >> 6) & 0b11:
                    duration_units = 'days'
                response['time_periods'].append(
                    {
                        'duration': (result['data'][6 + x] & 0b111111),
                        'duration_units': duration_units
                    }
                )

        return response


def get_dcmi_management_controller_id(username=None, password=None, ip_address=None,
                                      port=BMC_PORT):
    """ Get DCMI management controller ID from remote BMC.

    Args:
        username (str): username to connect to BMC with.
        password (str): password to connect to BMC with.
        ip_address (str): BMC IP address.
        port (int): BMC port.

    Returns:
        str: the management controller ID.

    Raises:
        SynseException: IPMI command failed or provided invalid response.
    """
    id_string = ''

    # read the mgmt controller ID out in blocks of 16 bytes, up to the limit of 64 bytes
    with IpmiCommand(ip_address=ip_address, username=username, password=password,
                     port=port) as ipmicmd:
        for x in range(0, 4):
            result = ipmicmd.raw_command(netfn=0x2c, command=0x01, data=(0xdc, x * 0x10))
            if 'error' in result:
                raise SynseException(
                    'Error executing get DCMI controller ID command on {} : {}'.format(
                        ip_address, result['error'])
                )

            # byte 0 should always be 0xdc
            if result['data'][0] != 0xdc:
                raise SynseException(
                    'Error in response to get DCMI controller ID command on {}: Invalid '
                    'first byte.'.format(ip_address)
                )

            # byte 1 should be the string length - ignore as remaining bytes are 0x00 (null)

            # tack on the remaining characters to the id string
            id_string.join([chr(c) for c in result['data'][2:]])

    return id_string
