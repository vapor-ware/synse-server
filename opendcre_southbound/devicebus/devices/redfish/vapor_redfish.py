#!/usr/bin/env python
""" OpenDCRE Redfish Bridge

    Author:  Morgan Morley Mills
    Date:    01/12/2017

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
import logging

from redfish_connection import get_data
from redfish_connection import post_action
from redfish_connection import patch_data
from opendcre_southbound.errors import OpenDCREException


logger = logging.getLogger(__name__)


def find_sensors(links, timeout, username, password):
    """ Get sensors information on the remote system for initialization or
    forced scans.

    Args:
        links (list[str]): the list of links to connect to via HTTP
        timeout (int | float): the number of seconds a GET will wait for a
            connection before timing out on the request
        username (str): the username for basic HTTP authentication
        password (str): the password for basic HTTP authentication

    Returns:
        dict: Identifying sensors information from the remote system.
    """
    response = list()
    sensors = dict()

    try:
        sensors['thermal'] = get_data(
            link=links[0],
            timeout=timeout,
            username=username,
            password=password
        )
        sensors['power'] = get_data(
            link=links[1],
            timeout=timeout,
            username=username,
            password=password
        )
    except ValueError as e:
        unfound = ', '.join({'thermal', 'power'}.difference(sensors.keys()))
        logger.error('Information about sensors on {} schema(s) not retrieved on GET: {}'.format(unfound, e.message))
        raise OpenDCREException('Cannot retrieve sensor data on {} schema(s): {}'.format(unfound, e.message))

    try:
        counter = 0
        for data in sensors['thermal']['Fans']:
            response.append({
                'device_id': format(counter, '04x'),
                'device_type': 'fan_speed',
                'device_info': data['Name']
            })
            counter += 1
        for data in sensors['thermal']['Temperatures']:
            response.append({
                'device_id': format(counter, '04x'),
                'device_type': 'temperature',
                'device_info': data['Name']
            })
            counter += 1
        for data in sensors['power']['Voltages']:
            response.append({
                'device_id': format(counter, '04x'),
                'device_type': 'voltage',
                'device_info': data['Name']
            })
            counter += 1
        for data in sensors['power']['PowerSupplies']:
            response.append({
                'device_id': format(counter, '04x'),
                'device_type': 'power_supply',
                'device_info': data['Name']
            })
            counter += 1
        return response
    except KeyError as e:
        logger.error('Sensor data not retrieved: {}'.format(e.message))
        raise OpenDCREException('Cannot retrieve sensor data: {}'.format(e.message))


def get_power(links, timeout, username, password):
    """ Get power information from the remote system.

    Args:
        links (list[str]): the list of links to connect to via HTTP
        timeout (int | float): the number of seconds a GET will wait for a
            connection before timing out on the request
        username (str): the username for basic HTTP authentication
        password (str): the password for basic HTTP authentication

    Returns:
        dict: Power information from the remote system.
    """
    response = dict()
    power_data = dict()

    try:
        power_data['power'] = get_data(
            link=links[1],
            timeout=timeout,
            username=username,
            password=password
        )
        power_data['systems'] = get_data(
            link=links[0],
            timeout=timeout,
            username=username,
            password=password
        )
    except ValueError as e:
        unfound = ', '.join({'power', 'systems'}.difference(power_data.keys()))
        logger.error('No data retrieved for {} schema(s) on GET: {}'.format(unfound, e.message))
        raise OpenDCREException('Cannot retrieve data from {} schema(s): {}'.format(unfound, e.message))

    try:
        response['power_status'] = power_data['systems']['PowerState'].lower()
        power_data['power'] = power_data['power']['PowerControl'][0]
        if float(power_data['power']['PowerConsumedWatts']) > float(power_data['power']['PowerLimit']['LimitInWatts']):
            response['over_current'] = True
        else:
            response['over_current'] = False
        response['power_ok'] = True if power_data['power']['Status']['Health'].lower() == 'ok' else False
        response['input_power'] = float(power_data['power']['PowerConsumedWatts'])
        return response
    except KeyError as e:
        logger.error('Incomplete or no data from GET on systems and power schemas'.format(e.message))
        raise OpenDCREException('Cannot retrieve power data.'.format(e.message))


def set_power(power_action, links, timeout, username, password):
    """ Set power state on the remote system.

    Args:
        power_action (str): 'on'/'off'/'cycle' - the state of the power of the
            remote device
        links (list[str]): the list of links to connect to via HTTP
        timeout (int | float): the number of seconds a POST will wait for a
            connection before timing out on the request
        username (str): the username for basic HTTP authentication
        password (str): the password for basic HTTP authentication

    Returns:
        dict: Power information from the remote system.
    """
    action_link = links[0] + '/Actions/ComputerSystem.Reset'
    _payload = str()

    if power_action.lower() == 'on':
        _payload = 'On'
    elif power_action.lower() == 'off':
        _payload = 'ForceOff'
    elif power_action.lower() == 'cycle':
        _payload = 'ForceRestart'

    if _payload:
        _payload = {'ResetType': _payload}
        try:
            post_action(
                link=action_link,
                payload=_payload,
                timeout=timeout,
                username=username,
                password=password
            )
            response = get_power(
                links=links,
                timeout=timeout,
                username=username,
                password=password
            )
            return response
        except ValueError as e:
            logger.error('Power not set with POST or response not returned on GET: {}'.format(e.message))
            raise OpenDCREException('Power cannot be set. POST error or GET error: {}'.format(e.message))
    else:
        logger.error('No payload data for POST on systems schema. Power cannot be set.')
        raise ValueError('No payload data for POST action. Power cannot be set.')


def get_asset(links, timeout, username, password):
    """ Get asset information from the remote system.

    Args:
        links (list[str]): the list of links to connect to via HTTP
        timeout (int | float): the number of seconds a GET will wait for a
            connection before timing out on the request
        username (str): the username for basic HTTP authentication
        password (str): the password for basic HTTP authentication

    Returns:
        dict: Asset information from the remote system.
    """
    response = dict()
    asset_data = dict()

    try:
        asset_data['chassis'] = get_data(
            link=links[0],
            timeout=timeout,
            username=username,
            password=password
        )
        asset_data['systems'] = get_data(
            link=links[1],
            timeout=timeout,
            username=username,
            password=password
        )
        asset_data['bmc'] = get_data(
            link=links[2],
            timeout=timeout,
            username=username,
            password=password
        )
    except ValueError as e:
        expected_keys = ['chassis', 'systems', 'bmc']
        unfound = ', '.join(set(expected_keys).difference(asset_data.keys()))
        logger.error('No data retrieved for {} schema(s) on GET: {}'.format(unfound, e.message))
        raise OpenDCREException('Cannot retrieve data from {} schema(s): {}'.format(unfound, e.message))

    try:
        response['chassis_info'] = {}
        response['chassis_info']['chassis_type'] = asset_data['chassis']['ChassisType']
        response['chassis_info']['part_number'] = asset_data['chassis']['PartNumber']
        response['chassis_info']['serial_number'] = asset_data['chassis']['SerialNumber']
        response['board_info'] = {}
        response['board_info']['manufacturer'] = asset_data['systems']['Manufacturer']
        response['board_info']['part_number'] = asset_data['systems']['PartNumber']
        response['board_info']['product_name'] = asset_data['systems']['Model']
        response['board_info']['serial_number'] = asset_data['systems']['SerialNumber']
        response['product_info'] = {}
        response['product_info']['manufacturer'] = 'unknown'  # NO BMC MANUFACTURER
        response['product_info']['part_number'] = 'unknown'  # NO BMC PART NUMBER
        response['product_info']['product_name'] = asset_data['bmc']['Model']
        response['product_info']['serial_number'] = 'unknown'  # NO BMC SERIAL NUMBER
        response['product_info']['version'] = asset_data['bmc']['FirmwareVersion']
        response['product_info']['asset_tag'] = asset_data['chassis']['AssetTag']
        return response
    except KeyError as e:
        logger.error('Incomplete asset data from GET on chassis, systems, and bmc schemas: {}'.format(e.message))
        raise OpenDCREException('Asset data cannot be retrieved: {}'.format(e.message))


def get_led(links, timeout, username, password):
    """ Retrieve remote system LED status.

    Args:
        links (list[str]): the list of links to connect to via HTTP
        timeout (int | float): the number of seconds a GET will wait for a
            connection before timing out on the request
        username (str): the username for basic HTTP authentication
        password (str): the password for basic HTTP authentication

    Returns:
        dict: LED Status as reported by remote system.
    """
    response = dict()

    try:
        led_status = get_data(
            link=links[0],
            timeout=timeout,
            username=username,
            password=password
        )
    except ValueError as e:
        logger.error('No data retrieved for LED status on GET of chassis schema: {}'.format(e.message))
        raise OpenDCREException('Cannot retrieve data from chassis schema: {}'.format(e.message))

    try:
        led_status = led_status['IndicatorLED'].lower()
        response['led_state'] = 'on' if led_status == 'lit' else led_status
        return response
    except KeyError as e:
        logger.error('Incomplete or no data for LED from GET on chassis schema. {} not found.'.format(e.message))
        raise OpenDCREException('Incomplete or no data from chassis schema. {} not found.'.format(e.message))


def set_led(led_state, links, timeout, username, password):
    """ Turn the remote system LED on or off.

    Args:
        led_state (str): the state to set the led to on the remote device
        links (list[str]): the list of links to connect to via HTTP
        timeout (int | float): the number of seconds a PATCH will wait for
            a connection before timing out on the request
        username (str): the username for basic HTTP authentication
        password (str): the password for basic HTTP authentication

    Returns:
        dict: LED State as set.
    """
    _payload = {'IndicatorLED': led_state}

    try:
        patch_data(
            link=links[0],
            payload=_payload,
            timeout=timeout,
            username=username,
            password=password,
        )
        response = get_led(links=links, timeout=timeout, username=username, password=password)
        return response
    except ValueError as e:
        logger.error('LED state not set on PATCH or response not returned on GET: {}'.format(e.message))
        raise OpenDCREException('LED state cannot be set. POST error or GET error: {}'.format(e.message))


def get_thermal_sensor(device_type, device_name, links, timeout, username, password):
    """ Get thermal sensor information from remote host.

    Args:
        device_type (str): the type of device to get information about on
            the remote system.
        device_name (str): the name of the device to get information about
            on the remote system.
        links (list[str]): the list of links to connect to via HTTP
        timeout (int | float): the number of seconds a GET will wait for a
            connection before timing out on the request
        username (str): the username for basic HTTP authentication
        password (str): the password for basic HTTP authentication

    Returns:
        dict: Thermal sensor information from the remote system.
    """
    response = dict()

    try:
        thermal_sensors = get_data(
            link=links[0],
            timeout=timeout,
            username=username,
            password=password
        )
    except ValueError as e:
        logger.error('No data retrieved on GET of thermal schema: {}'.format(e.message))
        raise OpenDCREException('Cannot retrieve data from thermal schema: {}'.format(e.message))

    try:
        thermal_sensors = thermal_sensors[device_type]
        for device in thermal_sensors:
            if device['Name'] == device_name:
                device_health = device['Status']['Health'].lower()
                response['health'] = 'ok' if device_health == 'ok' else device_health
                response['states'] = [] if response['health'] == 'ok' else [device['Status']['State'].lower()]
                if device_type == 'Fans':
                    response['speed_rpm'] = float(device['Reading'])
                elif device_type == 'Temperatures':
                    response['temperature_c'] = float(device['ReadingCelsius'])
        if response:
            return response
        else:
            logger.error('Device information not a match to devices from GET on thermal schema.')
            raise ValueError('No device matching information from GET on thermal schema.')
    except KeyError as e:
        logger.error('Incomplete data for sensor reading from GET on thermal schema: {}'.format(e.message))
        raise OpenDCREException('Incomplete data from thermal schema. Sensor information not found: {}'.format(e.message))


def get_power_sensor(device_type, device_name, links, timeout, username, password):
    """ Get power sensor information from remote host.

    Args:
        device_type (str): 'Voltages' for a voltage device, 'PowerSupplies'
            for a power_supply device
        device_name (str): the name of the device.
        links (list[str]): the list of links to connect to via HTTP
        timeout (int | float): the number of seconds a GET will wait for a
            connection before timing out on the request
        username (str): the username for basic HTTP authentication
        password (str): the password for basic HTTP authentication

    Returns:
        dict: Power sensor information from  the remote system.
    """
    response = dict()

    try:
        power_sensors = get_data(
            link=links[0],
            timeout=timeout,
            username=username,
            password=password
        )
    except ValueError as e:
        logger.error('No data retrieved on GET of power schema: {}'.format(e.message))
        raise OpenDCREException('Cannot retrieve data from power schema: {}'.format(e.message))

    try:
        power_sensors = power_sensors[device_type]
        for device in power_sensors:
            if device['Name'] == device_name:
                response['health'] = 'ok' if device['Status']['Health'].lower() == 'ok' \
                    else device['Status']['Health'].lower()
                response['states'] = [] if response['health'] == 'ok' else [device['Status']['State'].lower()]
                if device_type == 'Voltages':
                    response['voltage'] = float(device['ReadingVolts'])
        if response:
            return response
        else:
            logger.error('Device information not a match to devices from GET on power schema.')
            raise ValueError('No device matching information from GET on power schema.')
    except KeyError as e:
        logger.error('Incomplete data for sensor reading from GET on power schema: {}'.format(e.message))
        raise OpenDCREException('Incomplete data from power schema. Sensor information not found: {}'.format(e.message))


def get_boot(links, timeout, username, password):
    """ Get boot target from remote host.

    Args:
        links (list[str]): the list of links to connect to via HTTP
        timeout (int | float): the number of seconds a GET will wait for
            a connection before timing out on the request
        username (str): the username for basic HTTP authentication
        password (str): the password for basic HTTP authentication

    Returns:
        dict: Boot target information from the remote system.
    """
    response = dict()

    try:
        boot_data = get_data(
            link=links[0],
            timeout=timeout,
            username=username,
            password=password
        )
    except ValueError as e:
        logger.error('No data retrieved on GET of systems schema: {}'.format(e.message))
        raise OpenDCREException('Cannot retrieve data from systems schema: {}'.format(e.message))

    try:
        boot_data = boot_data['Boot']
        response['target'] = 'no_override' if boot_data['BootSourceOverrideTarget'].lower() == 'none' \
            else boot_data['BootSourceOverrideTarget'].lower()
        return response
    except KeyError as e:
        logger.error('Incomplete or no data for boot target reading from GET on systems schema: {}'.format(e.message))
        raise KeyError('Incomplete or no data from systems schema. {} not found.'.format(e.message))


def set_boot(target, links, timeout, username, password):
    """ Get boot target from remote host.

    Args:
        target (str): the value to change boot target to
        links (list[str]): the list of links to connect to via HTTP
        timeout (int | float): the number of seconds a GET/PATCH will wait for
            a connection before timing out on the request
        username (str): the username for basic HTTP authentication
        password (str): the password for basic HTTP authentication

    Returns:
        dict: Boot target information from the remote system.
    """
    response = dict()

    try:
        # connects to find out if BootSourceOverideEnabled is Disabled:
        current_boot = get_data(
            link=links[0],
            timeout=timeout,
            username=username,
            password=password
        )
    except ValueError as e:
        logger.error('No data retrieved on GET of systems schema: {}'.format(e.message))
        raise OpenDCREException('Cannot retrieve data from systems schema: {}'.format(e.message))

    try:
        current_boot = current_boot['Boot']

        if str(current_boot['BootSourceOverrideEnabled']).lower() != 'disabled':
            boot_target = 'None' if target == 'no_override' else target.capitalize()
            current_target = current_boot['BootSourceOverrideTarget'].lower()
            # if there is no need to patch to BootSourceOverrideTarget, this avoids making the requests.
            if current_target != boot_target.lower():
                _payload = {'Boot': {'BootSourceOverrideTarget': boot_target}}

                try:
                    patch_data(
                        link=links[0],
                        payload=_payload,
                        timeout=timeout,
                        username=username,
                        password=password
                    )
                    new_boot = get_boot(
                        links=links,
                        timeout=timeout,
                        username=username,
                        password=password
                    )
                except ValueError as e:
                    logger.error('LED state not set on PATCH or response not returned on GET: {}'.format(e.message))
                    raise OpenDCREException('LED state cannot be set. POST error or GET error: {}'.format(e.message))

                response['target'] = new_boot['target']

            else:
                response['target'] = 'no_override' if current_target == 'none' else current_target

            return response

        else:
            logger.error('Boot target unable to be overridden because BootTargetOverride is disabled on remote system.')
            raise ValueError('Cannot override boot target because BootTargetOverride is disabled on remote system.')

    except KeyError as e:
        logger.error('Incomplete data for boot target from GET on systems schema. {} not found'.format(e.message))
        raise OpenDCREException('Incomplete or no data for boot from systems schema. {} not found.'.format(e.message))
