#!/usr/bin/env python
"""
   OpenDCRE IPMI Support
   Author:  andrew
   Date:    2/23/2016 - Reorganize IPMI capabilities into separate file.

        \\//
         \/apor IO

Copyright (C) 2015-16  Vapor IO

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
import vapor_ipmi
import logging
import json
from definitions import *
from errors import *
from pyghmi.exceptions import *

logger = logging.getLogger()


def scan_ipmi(config_file=None):
    """ Open the BMC_CONFIG file and create a dictionary of all of the boards
    and devices available.

    Args:
        config_file: (String) The file name of the BMC configuration to read.

    Returns: (dict) A dictionary of the IPMI boards and devices determined by IPMI.

    """
    try:
        bmc_config = open('/opendcre/'+config_file, 'r')
        bmcs = json.load(bmc_config)
    except (IOError, AttributeError, ValueError):
        logger.exception("Unable to open or process BMC Configuration file. (%s)")
        return dict()

    i = 1
    for bmc in bmcs['bmcs']:
        bmc['board_id'] = IPMI_BOARD_ID | i     # for easier retrieval
        bmc['auth_type'] = bmc['auth_type']
        bmc['integrity_type'] = bmc['integrity_type']
        bmc['encryption_type'] = bmc['encryption_type']

        board_record = dict()
        board_record['board_id'] = format(IPMI_BOARD_ID | i, "08x")
        board_record['devices'] = [{'device_id': '0100', 'device_type': 'power'},
                                   {'device_id': '0200', 'device_type': 'system'},
                                   {'device_id': '0300', 'device_type': 'led'}]
        i += 1
        sensors = dict()
        try:
            sensors = vapor_ipmi.sensors(username=str(bmc['username']), password=str(bmc['password']),
                                         ip_address=str(bmc['bmc_ip']), ipmi20_enabled=True,
                                         ipmi20_auth=bmc['auth_type'],
                                         ipmi20_integrity=bmc['integrity_type'],
                                         ipmi20_encryption=bmc['encryption_type'])
        except (OpenDcreException, IpmiException) as e:
            logger.error("Unable to retrieve sensors for BMC: %s - %s", bmc['bmc_ip'], e.message)
        except ValueError:
            logger.exception("Invalid string in configuration file for BMC: %s", bmc['bmc_ip'])

        for sensor in sensors:
            if sensor['sensor_type'].lower() in ['temperature', 'fan']:
                if sensor['sensor_type'].lower() == 'temperature':
                    sensor_type = 'temperature'
                else:
                    sensor_type = 'fan_speed'
                board_record['devices'].append({'device_id': format(sensor['sensor_number'], "04x"),
                                                'device_type': sensor_type,
                                               'device_info': sensor['id_string']})
        bmc['board_record'] = board_record
    return bmcs


def is_ipmi_board(board_id):
    """ Determine if a board_id corresponds to an IPMI board.

    Args:
        board_id: (int) the board id to check.

    Returns:
        True if board_id is an IPMI board, False otherwise.
    """
    return True if board_id & IPMI_BOARD_ID else False


def get_ipmi_bmc_info(board_id=None, config=None):
    """ Get BMC configuration for a given board id.

    Args:
        board_id: The board ID to get IPMI BMC config for.
        config: The app config for the endpoint, containing the BMC info.

    Returns: The board record, if available, or None.

    """
    if 'bmcs' in config['BMCS']:
        for bmc in config['BMCS']['bmcs']:
            if board_id == bmc['board_id'] and 'board_record' in bmc:
                return bmc
    return None


def control_ipmi_power(board_id, device_id, power_action, config=None):
    """ Control the power on a device via IPMI.

    Args:
        board_id: The board_id of the device to control.
        device_id: The device_id of the device to control.
        power_action: The action to take - supported: "on", "off", "cycle", "status"
        config: The app config for the endpoint, containing the BMC info.

    Returns: (dict) Power Status regardless of command.

    Raises: (ValueError, vapor_ipmi.IpmiException) if power control is not possible.

    """
    if power_action not in ['on', 'off', 'cycle', 'status']:
        raise ValueError("Invalid IPMI power action {} for board {} device {}.".format(power_action, str(board_id),
                                                                                       str(device_id)))

    bmc_info = get_ipmi_bmc_info(board_id, config)
    if bmc_info is not None:
        for device in bmc_info['board_record']['devices']:
            if format(device_id, "04x") == device['device_id'] and device['device_type'] == 'power':
                return vapor_ipmi.power(username=bmc_info['username'], password=bmc_info['password'],
                                        ipmi20_enabled=True,
                                        ipmi20_auth=bmc_info['auth_type'],
                                        ipmi20_integrity=bmc_info['integrity_type'],
                                        ipmi20_encryption=bmc_info['encryption_type'],
                                        ip_address=bmc_info['bmc_ip'], cmd=power_action)

    raise ValueError("BMC or power device not found when trying to power control board: {} device: {} action: {})".
                     format(str(board_id),
                            str(device_id),
                            str(power_action)))


def get_ipmi_asset_info(board_id, device_id, config=None):
    """ Get asset information from IPMI for a given board and device.

    Args:
        board_id: The board_id to get asset information for.
        device_id: The device to get asset information for, must be of device_type 'system'.
        config: The app config for the endpoint, containing the BMC info.

    Returns: (dict) Asset information about the given device.

    Raises: (ValueError, vapor_ipmi.IpmiException) if the asset information command fails or is not possible.

    """
    bmc_info = get_ipmi_bmc_info(board_id, config)
    if bmc_info is not None:
        for device in bmc_info['board_record']['devices']:
            if format(device_id, "04x") == device['device_id'] and device['device_type'] == 'system':
                asset_data = vapor_ipmi.get_inventory(username=bmc_info['username'], password=bmc_info['password'],
                                                      ipmi20_enabled=True,
                                                      ipmi20_auth=bmc_info['auth_type'],
                                                      ipmi20_integrity=bmc_info['integrity_type'],
                                                      ipmi20_encryption=bmc_info['encryption_type'],
                                                      ip_address=bmc_info['bmc_ip'])
                asset_data['bmc_ip'] = bmc_info['bmc_ip']
                return asset_data

    raise ValueError("BMC or power device not found when trying to get asset info for board: {} device: {})".
                     format(str(board_id),
                            str(device_id)))


def set_ipmi_boot_target(board_id, device_id, target, config=None):
    """ Set the boot target via IPMI for the given board and device ID.

    Args:
        board_id: The board id to set boot target for.
        device_id: The device id to set boot target for.  Must be of device_type 'system'.
        target: The boot target to set, must be in 'no_override' (don't override the BIOS boot target),
                                                    'pxe' (force PXE boot)
                                                    'hdd' (force HDD boot)
        config: The app config for the endpoint, containing the BMC info.

    Returns: The boot target of the system.

    """
    bmc_info = get_ipmi_bmc_info(board_id, config)
    if bmc_info is not None:
        for device in bmc_info['board_record']['devices']:
            if format(device_id, "04x") == device['device_id'] and device['device_type'] == 'system':
                return vapor_ipmi.set_boot(username=bmc_info['username'], password=bmc_info['password'],
                                           ipmi20_enabled=True,
                                           ipmi20_auth=bmc_info['auth_type'],
                                           ipmi20_integrity=bmc_info['integrity_type'],
                                           ipmi20_encryption=bmc_info['encryption_type'],
                                           ip_address=bmc_info['bmc_ip'],
                                           target=target)

    raise ValueError("BMC or system device not found when trying to get boot target for board: {} device: {})".
                     format(str(board_id),
                            str(device_id)))


def get_ipmi_boot_target(board_id, device_id, config=None):
    """ Get the boot target via IPMI for the given board and device ID.

    Args:
        board_id: The board id to get boot target for.
        device_id: The device id to get boot target for.  Must be of device_type 'system'.
        config: The app config for the endpoint, containing the BMC info.

    Returns: The boot target of the system.

    """
    bmc_info = get_ipmi_bmc_info(board_id, config)
    if bmc_info is not None:
        for device in bmc_info['board_record']['devices']:
            if format(device_id, "04x") == device['device_id'] and device['device_type'] == 'system':
                return vapor_ipmi.get_boot(username=bmc_info['username'], password=bmc_info['password'],
                                           ipmi20_enabled=True,
                                           ipmi20_auth=bmc_info['auth_type'],
                                           ipmi20_integrity=bmc_info['integrity_type'],
                                           ipmi20_encryption=bmc_info['encryption_type'],
                                           ip_address=bmc_info['bmc_ip'])

    raise ValueError("BMC or system device not found when trying to get boot target for board: {} device: {})".
                     format(str(board_id),
                            str(device_id)))


def read_ipmi_sensor(board_id, device_id, device_type, config=None):
    """ Get a sensor reading from the given board_id/device_id via IPMI.

    Args:
        board_id: The board_id to get sensor reading from.
        device_id: The device_id to get sensor reading from.
        device_type: The type of sensor to read.
        config: The app config for the endpoint, containing the BMC info.

    Returns: (dict) Sensor reading dictionary.

    Raises: (ValueError, vapor_ipmi.IpmiException) if sensor reading is not possible.

    """
    if device_type not in ['temperature', 'fan_speed']:
        raise ValueError("Unsupported IPMI sensor type '{}' given for board {} and device {}.".format(device_type,
                                                                                                      str(board_id),
                                                                                                      str(device_id)))

    bmc_info = get_ipmi_bmc_info(board_id, config)
    if bmc_info is not None:
        for device in bmc_info['board_record']['devices']:
            if format(device_id, "04x") == device['device_id'] and device_type == device['device_type']:
                reading = vapor_ipmi.read_sensor(username=bmc_info['username'], password=bmc_info['password'],
                                                 ipmi20_enabled=True,
                                                 ipmi20_auth=bmc_info['auth_type'],
                                                 ipmi20_integrity=bmc_info['integrity_type'],
                                                 ipmi20_encryption=bmc_info['encryption_type'],
                                                 ip_address=bmc_info['bmc_ip'], sensor_name=device['device_info'])

                if device_type == 'temperature':
                    return {'temperature_c': reading['sensor_reading']}
                elif device_type == 'fan_speed':
                    return {'speed_rpm': reading['sensor_reading']}

    raise ValueError("BMC or sensor not found when trying to read board {} sensor {} ({})".format(str(board_id),
                                                                                                  str(device_id),
                                                                                                  str(device_type)))


def get_ipmi_led_state(board_id, device_id, config=None):
    """ Get LED state via IPMI for a given board and device.

    Args:
        board_id: The board_id to get LED state information for.
        device_id: The device to get LED state information for, must be of device_type 'system'.
        config: The app config for the endpoint, containing the BMC info.

    Returns: (dict) LED state information about the given device.

    Raises: (ValueError, vapor_ipmi.IpmiException) if the LED state information command fails or is not possible.

    """
    bmc_info = get_ipmi_bmc_info(board_id, config)
    if bmc_info is not None:
        for device in bmc_info['board_record']['devices']:
            if format(device_id, "04x") == device['device_id'] and device['device_type'] == 'led':
                led_data = vapor_ipmi.get_identify(username=bmc_info['username'], password=bmc_info['password'],
                                                   ipmi20_enabled=True,
                                                   ipmi20_auth=bmc_info['auth_type'],
                                                   ipmi20_integrity=bmc_info['integrity_type'],
                                                   ipmi20_encryption=bmc_info['encryption_type'],
                                                   ip_address=bmc_info['bmc_ip'])
                led_data['led_color'] = "unknown"
                led_data['led_state'] = "off" if led_data['led_state'] == 0 else "on"
                return led_data

    raise ValueError("BMC or power device not found when trying to get LED state info for board: {} device: {})".
                     format(str(board_id),
                            str(device_id)))


def set_ipmi_led_state(board_id, device_id, led_state, config=None):
    """ Set LED state via IPMI for a given board and device.

    Args:
        board_id: The board_id to set LED state information for.
        device_id: The device to set LED state information for, must be of device_type 'system'.
        led_state: The state to set the IPMI LED to (on, off).
        config: The app config for the endpoint, containing the BMC info.

    Returns: (dict) LED state information about the given device.

    Raises: (ValueError, vapor_ipmi.IpmiException) if the LED state command fails or is not possible.

    """
    bmc_info = get_ipmi_bmc_info(board_id, config)
    if bmc_info is not None:
        for device in bmc_info['board_record']['devices']:
            if format(device_id, "04x") == device['device_id'] and device['device_type'] == 'led':
                led_state = 0 if led_state.lower() == "off" else 1
                led_data = vapor_ipmi.set_identify(username=bmc_info['username'], password=bmc_info['password'],
                                                   ipmi20_enabled=True,
                                                   ipmi20_auth=bmc_info['auth_type'],
                                                   ipmi20_integrity=bmc_info['integrity_type'],
                                                   ipmi20_encryption=bmc_info['encryption_type'],
                                                   ip_address=bmc_info['bmc_ip'],
                                                   led_state=led_state)
                led_data['led_color'] = "unknown"
                led_data['led_state'] = "off" if led_data['led_state'] == 0 else "on"
                return led_data

    raise ValueError("BMC or power device not found when trying to set LED state info for board: {} device: {})".
                     format(str(board_id),
                            str(device_id)))
