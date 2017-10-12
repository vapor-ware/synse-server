#!/usr/bin/env python
""" Main blueprint for Synse. This contains the core endpoints
for Synse.

    Author: Erick Daniszewski
    Date:   09/24/2016

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
# pylint: disable=line-too-long

import copy
import json
import logging

from flask import Blueprint, current_app

import synse.constants as const
import synse.strings as _s_
from synse import definitions
from synse.devicebus.devices import (I2CDevice, IPMIDevice, PLCDevice,
                                     RedfishDevice, RS485Device, SnmpDevice)
from synse.errors import SynseException
from synse.location import get_chassis_location
from synse.utils import (check_valid_board, check_valid_board_and_device,
                         get_device_instance, get_device_type_code,
                         get_scan_cache, make_json_response, write_scan_cache)
from synse.vapor_common.utils.endpoint import make_url_builder
from synse.version import __api_version__

# add the api_version to the prefix
PREFIX = const.endpoint_prefix + __api_version__
url = make_url_builder(PREFIX)

core = Blueprint('core', __name__)
logger = logging.getLogger(__name__)


def _lookup_device_uuid(board_id):
    """ Lookup the UUID of a devicebus instance for a given board id/alias.

    Args:
        board_id (int | str): board id, or devicebus alias, to look up.

    Returns:
        str: the UUID of the devicebus interface if found.
        None: no devicebus interface matched the board id/alias.
    """
    device = get_device_instance(board_id)

    # unsupported device returns None
    if not isinstance(device, (PLCDevice, IPMIDevice, RS485Device, I2CDevice,
                               SnmpDevice, RedfishDevice)):
        return None

    uuid = None
    if device:
        uuid = str(device.device_uuid)
    return uuid


def _add_device_mapping(scan_result):
    """ Add device mapping to the internal scan cache.

    Args:
        scan_result (dict): results from the scan.

    Returns:
        dict: the scan results augmented with device interface ids.
    """
    res = copy.deepcopy(scan_result)
    for rack in res['racks']:
        for board in rack['boards']:
            board['device_interface'] = _lookup_device_uuid(int(board['board_id'], 16))
    return res


def _filter_cache_meta(cache):
    """ Filter out meta information from the cache.

    This filtering should be done before the cache is returned from any endpoint.
    It prevents internal cache annotations from being surfaced, making the scan
    results cleaner and less confusing to the endpoint consumer.

    Args:
        cache (dict): the cache as a dictionary.

    Returns:
        dict: the cache stripped of internal meta info.
    """
    for rack in cache['racks']:
        for board in rack['boards']:
            if 'device_interface' in board:
                del board['device_interface']
    return cache


def _merge_list(accumulator, l, key_name):
    """ Merge list l[key_name] into the accumulator[key_name] list.

    Args:
        accumulator (dict): a dict containing the current accumulation in
            accumulator[key_name]. also the merge result.
        l (dict): a dict containing the list to merge in at l[key_name].
        key_name (str): the name of the key common to both dicts, each of
            which is a list.

    Returns:
        dict: the accumulator dictionary.
    """
    # If there is no l or no key at l[key_name] there is nothing to merge.
    if not l or key_name not in l:
        return

    # If l[key_name] is None or length zero there is nothing to merge.
    if (l[key_name] is None) or (len(l[key_name]) == 0):
        return

    # Check for already accumulated list items to de-dup.
    if key_name not in accumulator[key_name]:
        # We have something to merge. If there is no list in the accumulator
        # at accumulator[key_name], make one.
        if key_name not in accumulator:
            accumulator[key_name] = list()
        accumulator[key_name].extend(l[key_name])


def _merge_scan_results(d, u):
    """ Merge two sets of scan results together.

    Args:
        d (dict): accumulator for merged results.
        u (dict): results to merge into d.

    Returns:
        dict: a dictionary resulting from the merge of the provided
            dictionaries.
    """
    if u is not None:
        # For every rack in u.
        if 'racks' in u:
            for u_rack in u['racks']:
                has_rack = False
                # Find rack in d.
                for d_rack in d['racks']:
                    if d_rack['rack_id'] == u_rack['rack_id']:
                        # Found the rack. Merge each of the following fields.
                        has_rack = True
                        _merge_list(d_rack, u_rack, 'boards')
                        _merge_list(d_rack, u_rack, 'hostnames')
                        _merge_list(d_rack, u_rack, 'ip_addresses')

                # First rack in the accumulator. Add it.
                if not has_rack:
                    if 'racks' not in d:
                        d['racks'] = list()
                    d['racks'].append(u_rack)
    return d


@core.route(url('/version/<rack_id>/<board_id>'), methods=['GET'])
def get_board_version(rack_id, board_id):
    """ Get the version information for the specified board.

    Args:
        rack_id (str): the rack id associated with the board.
        board_id (str): the board id to get version for.

    Returns:
        The version of the hardware and firmware for the given board.

    Raises:
        Returns a 500 error if the version command fails.
    """
    board_id = check_valid_board(board_id)

    cmd = current_app.config['CMD_FACTORY'].get_version_command({
        _s_.RACK_ID: rack_id,
        _s_.BOARD_ID: board_id
    })

    device = get_device_instance(board_id)
    response = device.handle(cmd)

    return make_json_response(response.get_response_data())


@core.route(url('/scan'), methods=['GET'])
def scan_all():
    """ Query for all boards and provide the active devices on each board.

    Returns:
        Active devices, ids and types from the queried board(s).

    Raises:
        Returns a 500 error if the scan command fails.
    """
    scan_response = {'racks': []}

    _cache = get_scan_cache()
    if _cache:
        return make_json_response(_filter_cache_meta(_cache))

    for _, device in current_app.config['DEVICES'].iteritems():
        cmd = current_app.config['CMD_FACTORY'].get_scan_all_command({
            _s_.FORCE: False
        })
        response = device.handle(cmd)
        scan_response = _merge_scan_results(scan_response, response.get_response_data())

    write_scan_cache(_add_device_mapping(scan_response))
    return make_json_response(scan_response)


@core.route(url('/scan/force'))
def force_scan():
    """ Force the scan of all racks, boards, and devices. This will ignore
    any existing cache. If the forced scan is successful, it will update the
    cache.

    Returns:
        Active devices, ids and types from the queried board(s).

    Raises:
        Returns a 500 error if the scan command fails.
    """
    scan_response = {'racks': []}

    for _, device in current_app.config['DEVICES'].iteritems():
        cmd = current_app.config['CMD_FACTORY'].get_scan_all_command({
            _s_.FORCE: True,
        })
        response = device.handle(cmd)
        scan_response = _merge_scan_results(scan_response, response.get_response_data())

    write_scan_cache(_add_device_mapping(scan_response))
    return make_json_response(scan_response)


@core.route(url('/scan/<rack_id>'), methods=['GET'])
@core.route(url('/scan/<rack_id>/<board_id>'), methods=['GET'])
def get_board_devices(rack_id, board_id=None):
    """ Query a specific rack or board and provide the active devices on
    the found board(s).

    Args:
        rack_id (str): the id of the rack to scan.
        board_id (str): the board id to scan. if the upper byte is 0x80 then
            all boards will be scanned.

    Returns:
        Active devices, numbers and types from the queried board(s).

    Raises:
        Returns a 500 error if the scan command fails.
    """
    # if there is no board_id, we are doing a scan on a rack.
    # FIXME: since scan by the rack is not supported yet, (v 1.3) we will
    # determine the rack results by filtering on the 'scanall' results.
    if board_id is None:
        scanall = scan_all()
        data = json.loads(scanall.data)
        for rack in data['racks']:
            if rack['rack_id'] == rack_id:
                return make_json_response({'racks': [rack]})
        raise SynseException('No rack found with id: {}'.format(rack_id))

    board_id = check_valid_board(board_id)

    # FIXME (etd) - unclear why this was temporarily disabled, we probably want
    # to re-enable.
    # FIXME: temporarily disabled scan cache
    # _cache = get_scan_cache()
    # if _cache:
    #    _cache = filter_cache_meta(_cache)
    #    for rack in _cache['racks']:
    #        if rack['rack_id'] == rack_id:
    #            for board in rack['boards']:
    #                if int(board['board_id'], 16) == board_id:
    #                    return make_json_response({'boards': [board]})
    #                else:
    #                    break

    cmd = current_app.config['CMD_FACTORY'].get_scan_command({
        _s_.RACK_ID: rack_id,
        _s_.BOARD_ID: board_id
    })

    device = get_device_instance(board_id)
    response = device.handle(cmd)

    return make_json_response(response.get_response_data())


@core.route(url('/read/<device_type>/<rack_id>/<board_id>/<device_id>'), methods=['GET'])
def read_device(rack_id, device_type, board_id, device_id):
    """ Get a device reading for the specified device type on the specified device.

    Args:
        rack_id (str): the id of the rack where target board & device reside.
        device_type (str): corresponds to the type of device to get a reading for.
            It must match the actual type of device that is present on the bus,
            and is used to interpret the raw device reading.
        board_id (str): the id of the board where the target device resides.
        device_id (str): specifies which device should be polled for device reading.

    Returns:
        Interpreted and raw device reading, based on the specified device type.

    Raises:
        Returns a 500 error if the read command fails.
    """
    board_id, device_id = check_valid_board_and_device(board_id, device_id)

    cmd = current_app.config['CMD_FACTORY'].get_read_command({
        _s_.RACK_ID: rack_id,
        _s_.BOARD_ID: board_id,
        _s_.DEVICE_ID: device_id,
        _s_.DEVICE_TYPE: get_device_type_code(device_type.lower()),
        _s_.DEVICE_TYPE_STRING: device_type.lower()
    })

    device = get_device_instance(board_id)
    response = device.handle(cmd)

    return make_json_response(response.get_response_data())


@core.route(url('/power/<rack_id>/<board_id>/<device_id>/<power_action>'), methods=['GET'])
@core.route(url('/power/<device_type>/<rack_id>/<board_id>/<device_id>/<power_action>'), methods=['GET'])
@core.route(url('/power/<rack_id>/<board_id>/<device_id>'), methods=['GET'])
def power_control(power_action='status', rack_id=None, board_id=None, device_id=None, device_type='power'):
    """ Power control for the given rack, board, and device.

    Args:
        power_action (str): may be on/off/cycle/status and corresponds to the
            action to take.
        rack_id (str): the id of the rack which contains the board to accept
            the power control command.
        board_id (str): the id of the board which contains the device that
            accepts power control commands.
        device_id (str): the id of the device which accepts power control
            commands.
        device_type (str): the type of device to accept power control command
            for. (default: power)

    Returns:
        Power status of the given device.

    Raises:
        Returns a 500 error if the power command fails.
    """
    board_id, device_id = check_valid_board_and_device(board_id, device_id)

    if rack_id.lower() in [_s_.PWR_ON, _s_.PWR_OFF, _s_.PWR_CYCLE, _s_.PWR_STATUS]:
        # FIXME: (etd) - we should probably depricate the 'old' form described here
        #   for both cleanliness and API unity.
        # for backwards-compatibility, we allow the command to come in as:
        # power_action/board_id/device_id
        # therefore, if we see a power action in the rack_id field, then
        # we need to rearrange the parameters
        power_action = rack_id

    cmd = current_app.config['CMD_FACTORY'].get_power_command({
        _s_.BOARD_ID: board_id,
        _s_.DEVICE_ID: device_id,
        _s_.DEVICE_TYPE: get_device_type_code(device_type.lower()),
        _s_.POWER_ACTION: power_action
    })

    device = get_device_instance(board_id)
    response = device.handle(cmd)

    return make_json_response(response.get_response_data())


@core.route(url('/asset/<rack_id>/<board_id>/<device_id>'), methods=['GET'])
def asset_info(rack_id, board_id, device_id):
    """ Get asset information for a given board and device.

    Args:
        rack_id (str): the id of the rack where the target board resides.
        board_id (str): the board number to get asset information for.
        device_id (str): the device number to get asset information for (the
            device must have a device_type of 'system').

    Returns:
        Asset information about the given device.

    Raises:
        Returns a 500 error if the asset command fails.
    """
    board_id, device_id = check_valid_board_and_device(board_id, device_id)

    cmd = current_app.config['CMD_FACTORY'].get_asset_command({
        _s_.BOARD_ID: board_id,
        _s_.DEVICE_ID: device_id,
        _s_.DEVICE_TYPE: get_device_type_code(const.DEVICE_SYSTEM),
        _s_.RACK_ID: rack_id
    })

    device = get_device_instance(board_id)
    response = device.handle(cmd)

    return make_json_response(response.get_response_data())


@core.route(url('/boot_target/<rack_id>/<board_id>/<device_id>/<target>'), methods=['GET'])
@core.route(url('/boot_target/<rack_id>/<board_id>/<device_id>'), methods=['GET'])
def boot_target(rack_id, board_id, device_id, target=None):
    """ Get or set the boot target for a given board and device.

    Args:
        rack_id (str): the id of the rack where the target board resides.
        board_id (str): the board id to get/set boot target for.
        device_id (str): the device id to get/set boot target for (the device
            must have a device_type of 'system').
        target (str): the boot target to choose. if not specified, the
            default behavior is to get the boot target info. valid values
            for boot target are 'pxe', 'hdd', and 'no_override'.

    Returns:
        Boot target of the device.

    Raises:
        Returns a 500 error if the boot target command fails.
    """
    board_id, device_id = check_valid_board_and_device(board_id, device_id)

    if target is not None and target not in [_s_.BT_PXE, _s_.BT_HDD, _s_.BT_NO_OVERRIDE]:
        logger.error('Boot Target: Invalid boot target specified: %s board_id: %s device_id: %s', target, board_id,
                     device_id)
        raise SynseException('Invalid boot target specified.')

    cmd = current_app.config['CMD_FACTORY'].get_boot_target_command({
        _s_.BOARD_ID: board_id,
        _s_.DEVICE_ID: device_id,
        _s_.DEVICE_TYPE: get_device_type_code(const.DEVICE_SYSTEM),
        _s_.BOOT_TARGET: target if target is not None else 'status',
        _s_.RACK_ID: rack_id
    })

    device = get_device_instance(board_id)
    response = device.handle(cmd)

    return make_json_response(response.get_response_data())


@core.route(url('/location/<rack_id>/<board_id>/<device_id>'), methods=['GET'])
@core.route(url('/location/<rack_id>/<board_id>'), methods=['GET'])
def device_location(rack_id, board_id=None, device_id=None):  # pylint: disable=unused-argument
    """ Get the location of a device.

    This command is supported for PLC. Other devicebus types (IPMI, Redfish,
    SNMP, RS485, I2C) are not supported, so 'unknown' is returned.

    Args:
        rack_id (str): the id of the rack where the target board resides
        board_id (str): the board id to get location for. non-PLC boards
            are not supported.
        device_id (str): the device id to get location for. non-PLC devices
            are not supported.

    Returns:
        The location of device, if known.

    Raises:
        Returns a 500 error if the location command fails.
    """
    if device_id is not None:
        (board_id, device_id) = check_valid_board_and_device(board_id, device_id)
        if device_id > 0xFFFF:
            raise SynseException('Device number must be <= 0xFFFF')
    else:
        board_id = check_valid_board(board_id)

    try:
        # add validation on the board by finding its device instance. if this
        # is not a valid board, we raise an exception, as there is no valid
        # location for it
        get_device_instance(board_id)
    except Exception as e:
        raise e

    # physical (rack) location is not yet implemented in v1
    physical_location = {
        _s_.LOC_HORIZONTAL: _s_.LOC_UNKNOWN,
        _s_.LOC_VERTICAL: _s_.LOC_UNKNOWN,
        _s_.LOC_DEPTH: _s_.LOC_UNKNOWN
    }

    if device_id is not None:
        return make_json_response({
            _s_.PHYSICAL_LOC: physical_location,
            _s_.CHASSIS_LOC: get_chassis_location(device_id)
        })

    return make_json_response({
        _s_.PHYSICAL_LOC: physical_location
    })


def _chamber_led_control(board_id, device_id, led_state, rack_id, led_color, blink_state):
    """ Control the Vapor Chamber LED via PLC.

    Args:
        board_id (str): the board id of the LED controller for vapor_led.
        device_id (str): the device id of the LED controller for vapor_led.
        led_state (str): the state to set the specified LED to. valid states
            are: (on, off, no_override)
        rack_id (str): the id of the rack whose LED segment is to be controlled
            (MIN_RACK_ID..MAX_RACK_ID)
        led_color (str): the RGB hex value of the color to set the LED to, or
            'no_override'.
        blink_state (str): the blink state of the LED. valid blink states are:
            (blink, steady, no_override).
    """
    cmd = current_app.config['CMD_FACTORY'].get_chamber_led_command({
        _s_.BOARD_ID: board_id,
        _s_.DEVICE_ID: device_id,
        _s_.DEVICE_TYPE: get_device_type_code(const.DEVICE_VAPOR_LED),
        _s_.DEVICE_TYPE_STRING: const.DEVICE_VAPOR_LED,
        _s_.DEVICE_NAME: const.DEVICE_VAPOR_LED,
        _s_.RACK_ID: rack_id,
        _s_.LED_STATE: led_state,
        _s_.LED_COLOR: led_color,
        _s_.LED_BLINK_STATE: blink_state,
    })

    device = get_device_instance(board_id)
    response = device.handle(cmd)

    return make_json_response(response.get_response_data())


@core.route(url('/led/<rack_id>/<board_id>/<device_id>'), methods=['GET'])
@core.route(url('/led/<rack_id>/<board_id>/<device_id>/<led_state>'), methods=['GET'])
@core.route(url('/led/<rack_id>/<board_id>/<device_id>/<led_state>/<led_color>/<blink_state>'), methods=['GET'])
def led_control(rack_id, board_id, device_id, led_state=None, led_color=None, blink_state=None):
    """ Control an LED on system or Vapor Chamber wedge rack.

    System LEDs may only be turned on/off. Vapor Chamber wedge rack
    supports color.

    Args:
        rack_id (str): the rack id to control LED for.
        board_id (str): the board id to control LED for. IPMI boards only
            support on/off.
        device_id (str): the device id to control LED for. IPMI devices only
            support on/off.
        led_state (str): the state to set LED to (on/off/blink for PLC,
            on/off for IPMI).
        led_color (str): the hex RGB color to set LED to (for PLC wedge LED only).
        blink_state (str): the blink state (blink|steady|no_override) for PLC
            wedge LED only.

    Returns:
        LED state for chassis LED; LED state, color and blink state for PLC wedge LED.

    Raises:
        Returns a 500 error if the LED command fails.
    """
    board_id, device_id = check_valid_board_and_device(board_id, device_id)

    if led_state not in [_s_.LED_ON, _s_.LED_OFF, _s_.LED_NO_OVERRIDE, None]:
        logger.error('Invalid LED state {} provided for LED control.'.format(led_state))
        raise SynseException('Invalid LED state provided for LED control.')

    if led_color is not None and led_color != _s_.LED_NO_OVERRIDE:
        try:
            led_color_int = int(led_color, 16)
            if (led_color_int < 0x000000) or (led_color_int > 0xffffff):
                raise ValueError('LED Color must be between 0x000000 and 0xffffff.')
        except ValueError as e:
            raise SynseException('Invalid LED color specified. ({})'.format(e.message))

    if blink_state is not None and blink_state not in [_s_.LED_BLINK, _s_.LED_STEADY, _s_.LED_NO_OVERRIDE]:
        raise SynseException('Invalid blink state specified for LED.')

    elif (led_color is not None) and (blink_state is not None):
        if not const.get_board_type(board_id) == const.BOARD_TYPE_SNMP:
            return _chamber_led_control(board_id=board_id, device_id=device_id, led_state=led_state,
                                        rack_id=rack_id, led_color=led_color, blink_state=blink_state)

    cmd = current_app.config['CMD_FACTORY'].get_led_command({
        _s_.BOARD_ID: board_id,
        _s_.DEVICE_ID: device_id,
        _s_.DEVICE_TYPE: get_device_type_code(const.DEVICE_LED),
        _s_.DEVICE_TYPE_STRING: const.DEVICE_LED,
        _s_.DEVICE_NAME: const.DEVICE_LED,
        _s_.RACK_ID: rack_id,
        _s_.LED_STATE: led_state,
        _s_.LED_COLOR: led_color,
        _s_.LED_BLINK_STATE: blink_state,
    })

    device = get_device_instance(board_id)
    response = device.handle(cmd)

    return make_json_response(response.get_response_data())


@core.route(url('/fan/<rack_id>/<board_id>/<device_id>'), methods=['GET'])
@core.route(url('/fan/<rack_id>/<board_id>/<device_id>/<fan_speed>'), methods=['GET'])
def fan_control(rack_id, board_id, device_id, fan_speed=None):
    """ Control a fan on a system or Vapor Chamber.

    System fan may only be polled for status unless explicitly supported.

    Args:
        rack_id (str): the rack id to control fan for.
        board_id (str): the board id to control fan for.
        device_id (str): the device id to control fan for.
        fan_speed (str): the speed to set the fan to.

    Returns:
        The status of the fan; fan speed in RPM.

    Raises:
        Returns a 500 error if the fan command fails.
    """
    board_id, device_id = check_valid_board_and_device(board_id, device_id)

    # if we are reading the fan speed only, forward on to the device_read method and
    # pass along response
    if fan_speed is None:
        return read_device(rack_id, const.DEVICE_FAN_SPEED, board_id, device_id)

    if fan_speed != 'max':
        # max is a synse-server-internal only route. See gs3_2010_fan_controller.
        try:
            # Check that we have a positive integer.
            # We cannot check max here because max is fan motor specific.
            fan_speed_int = int(fan_speed)
            if fan_speed_int < 0:
                raise ValueError('Fan speed out of acceptable range.')
        except ValueError as e:
            raise SynseException('Error converting fan_speed to integer ({}).'.format(e))

    cmd = current_app.config['CMD_FACTORY'].get_fan_command({
        _s_.BOARD_ID: board_id,
        _s_.DEVICE_ID: device_id,
        _s_.DEVICE_TYPE: get_device_type_code(const.DEVICE_FAN_SPEED),
        _s_.DEVICE_NAME: const.DEVICE_FAN_SPEED,
        _s_.FAN_SPEED: fan_speed
    })

    device = get_device_instance(board_id)
    response = device.handle(cmd)

    return make_json_response(response.get_response_data())


@core.route(url('/host_info/<rack_id>/<board_id>/<device_id>'), methods=['GET'])
def host_info(rack_id, board_id, device_id):
    """ Get hostname(s) and ip address(es) for a given host.

    The host must be of type 'system'.

    Args:
        rack_id (str): the id of the rack where the target board resides.
        board_id (str): the board id to get host info for.
        device_id (str): the device id to get host info for.

    Returns:
        Hostname(s) and IP address(es) for the specified system.

    Raises:
        Returns a 500 error if the host info command fails.
    """
    board_id, device_id = check_valid_board_and_device(board_id, device_id)

    cmd = current_app.config['CMD_FACTORY'].get_host_info_command({
        _s_.BOARD_ID: board_id,
        _s_.DEVICE_ID: device_id,
        _s_.DEVICE_TYPE: get_device_type_code(const.DEVICE_SYSTEM),
        _s_.DEVICE_NAME: const.DEVICE_SYSTEM,
        _s_.RACK_ID: rack_id
    })

    device = get_device_instance(board_id)
    response = device.handle(cmd)

    return make_json_response(response.get_response_data())
