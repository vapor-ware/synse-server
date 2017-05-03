#!/usr/bin/env python
""" Main blueprint for OpenDCRE southbound. This contains the core endpoints
for OpenDCRE.

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
import logging
import copy
import json
from uuid import UUID

from flask import current_app, Blueprint, jsonify

from vapor_common.utils.endpoint import make_url_builder
import opendcre_southbound.constants as const
import opendcre_southbound.strings as _s_
from opendcre_southbound import definitions
from opendcre_southbound.errors import OpenDCREException
from opendcre_southbound.location import get_chassis_location
from opendcre_southbound.version import __api_version__
from opendcre_southbound.devicebus.devices import (
    PLCDevice,
    IPMIDevice,
    RS485Device,
    I2CDevice,
    SnmpDevice,
    RedfishDevice
)
from opendcre_southbound.utils import (
    check_valid_board,
    check_valid_board_and_device,
    get_device_type_code,
    get_scan_cache,
    write_scan_cache,
    get_device_instance
)

# add the api_version to the prefix
PREFIX = const.endpoint_prefix + __api_version__
url = make_url_builder(PREFIX)

core = Blueprint('core', __name__)
logger = logging.getLogger(__name__)


def _lookup_by_id_range(board_id):
    """ Lookup the device(s) for a given board by the board id.

    Args:
        board_id (int): board id to look up

    Returns:
        dict: a dictionary of all the devices which map to the given
            board id range.
    """
    device = get_device_instance(board_id)

    # unsupported device returns None
    if not isinstance(device, (PLCDevice, IPMIDevice, RS485Device, I2CDevice, SnmpDevice, RedfishDevice)):
        return None

    return {uid: dev for uid, dev in current_app.config['DEVICES'].iteritems() if isinstance(dev, device.__class__)}


# FIXME (etd) -- is this used? PyCharm seems to think that it is not used.
def get_device_interfaces(board_id):
    """ Get the configured device interface(s) which the board is determined to
    belong to.

    This determination is done by checking if the given board_id falls within
    the id range for the given configured devices. Any device for which the
    board_id falls within the id range is returned.

    Args:
        board_id (int): the id of the board to find the devicebus interface for

    Returns:
        list[DevicebusInterface]: the found devicebus interfaces, if any. If no
            interfaces are found, None is returned.
    """
    _cache = get_scan_cache()
    cache_modified = False
    if _cache:
        devices = None
        for rack in _cache['racks']:
            for board in rack['boards']:
                if 'device_interface' in board:
                    interface_ids = map(UUID, board['device_interface'])
                    devices = [current_app.config['DEVICES'].get(iid) for iid in interface_ids]
                else:
                    _devices = _lookup_by_id_range(board_id)

                    devices = _devices.values()
                    device_ids = _devices.keys()

                    board['device_interface'] = device_ids
                    cache_modified = True
                break

        if cache_modified:
            write_scan_cache(_cache)

    else:
        devices = _lookup_by_id_range(board_id).values()

    if not devices:
        # None is returned here in cases where no devices are found. the upstream caller
        # should handle this case appropriately, likely by raising an exception.
        return None
    else:
        return devices


def add_device_mapping(scan_result):
    """ Add device mapping to the internal scan cache.

    Args:
        scan_result (dict): results from the scan.

    Returns:
        dict: the scan results augmented with device interface ids
    """
    res = copy.deepcopy(scan_result)
    for rack in res['racks']:
        for board in rack['boards']:
            interfaces = _lookup_by_id_range(int(board['board_id'], 16)).keys()
            board['device_interface'] = map(str, interfaces)
    return res


def filter_cache_meta(cache):
    """ Filter out meta information from the cache.

    This filtering should be done before the cache is returned from any endpoint.
    It prevents internal cache annotations from being surfaced, making the scan
    results cleaner and less confusing to the endpoint consumer.

    Args:
        cache (dict): the cache as a dictionary

    Returns:
        dict: the cache stripped of meta info.
    """
    for rack in cache['racks']:
        for board in rack['boards']:
            if 'device_interface' in board:
                del board['device_interface']
    return cache


@core.route(url('/version/<rack_id>/<board_id>'), methods=['GET'])
def get_board_version(rack_id, board_id):
    """ Get board version given the specified board id.

    Args:
        rack_id (str): the rack id associated with the board (currently unused).
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

    return jsonify(response.data)


def _merge_list(accumulator, l, key_name):
    """Merge list l[key_name] into the accumulator[key_name] list.
    :param accumulator: A dict containing the current accumulation in
     accumulator[keyname]. Also the merge result.
    :param l: A dict containing the list to merge in at l[keyname].
    :param key_name: The name of the key common to both dicts, each of which is a list.
    :returns: The accumulator."""

    # If there is no l or no key at l[key_name] there is nothing to merge.
    if not l or key_name not in l:
        return

    # If l[keyname] is None or length zero there is nothing to merge.
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
    """ Merge two sets of scan results together
    :param d: Accumulator for merged results.
    :param u: Results to merge into u.
    """
    # For every rack in u.
    if u is not None:
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


@core.route(url('/scan'), methods=['GET'])
def scan_all():
    """ Query for all boards, and provide the active devices on each board.

    Returns:
        Active devices, numbers and types from the given board(s).

    Raises:
        Returns a 500 error if the scan command fails.
    """
    scan_response = {'racks': []}

    _cache = get_scan_cache()
    if _cache:
        return jsonify(filter_cache_meta(_cache))

    for _id, device in current_app.config['DEVICES'].iteritems():
        cmd = current_app.config['CMD_FACTORY'].get_scan_all_command({
            _s_.FORCE: False
        })
        response = device.handle(cmd)
        scan_response = _merge_scan_results(scan_response, response.data)

    write_scan_cache(add_device_mapping(scan_response))
    return jsonify(scan_response)


@core.route(url('/scan/force'))
def force_scan():
    """ Force the scan of all racks, boards, and devices. This will ignore
    any existing cache. If the forced scan is successful, it will update the
    cache.

    Returns:
        Active devices, numbers and types from the given board(s).

    Raises:
        Returns a 500 error if the scan command fails.
    """
    scan_response = {'racks': []}

    for _id, device in current_app.config['DEVICES'].iteritems():
        cmd = current_app.config['CMD_FACTORY'].get_scan_all_command({
            _s_.FORCE: True,
        })
        response = device.handle(cmd)
        scan_response = _merge_scan_results(scan_response, response.data)

    write_scan_cache(add_device_mapping(scan_response))
    return jsonify(scan_response)


@core.route(url('/scan/<rack_id>'), methods=['GET'])
@core.route(url('/scan/<rack_id>/<board_id>'), methods=['GET'])
def get_board_devices(rack_id, board_id=None):
    """ Query a specific board, given the board id, and provide the active
    devices on that board.

    Args:
        rack_id (str): The id of the rack where the target board resides
        board_id (str): the board number to dump. If the upper byte is 0x80 then
            all boards on the bus will be scanned.

    Returns:
        Active devices, numbers and types from the given board(s).

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
                return jsonify({'racks': [rack]})
        raise OpenDCREException('No rack found with id: {}'.format(rack_id))

    board_id = check_valid_board(board_id)

    """
    FIXME: temporarily disabled scan cache
    _cache = get_scan_cache()
    if _cache:
        _cache = filter_cache_meta(_cache)
        for rack in _cache['racks']:
            if rack['rack_id'] == rack_id:
                for board in rack['boards']:
                    if int(board['board_id'], 16) == board_id:
                        return jsonify({'boards': [board]})
                    else:
                        break
    """

    cmd = current_app.config['CMD_FACTORY'].get_scan_command({
        _s_.RACK_ID: rack_id,
        _s_.BOARD_ID: board_id
    })

    device = get_device_instance(board_id)
    response = device.handle(cmd)

    return jsonify(response.data)


@core.route(url('/read/<device_type>/<rack_id>/<board_id>/<device_id>'), methods=['GET'])
def read_device(rack_id, device_type, board_id, device_id):
    """ Get a device reading for the given board and port and device type.

    We could filter on the upper ID of board_id in case an unusual board number
    is provided; however, the bus should simply time out in these cases.

    Args:
        rack_id (str): The id of the rack where target board & device reside
        device_type (str): corresponds to the type of device to get a reading for.
            It must match the actual type of device that is present on the bus,
            and is used to interpret the raw device reading.
        board_id (str): specifies which Pi hat to get the reading from
        device_id (str): specifies which device of the Pi hat should be polled
            for device reading.

    Returns:
        Interpreted and raw device reading, based on the specified device type.

    Raises:
        Returns a 500 error if the read command fails.
    """
    board_id, device_id = check_valid_board_and_device(board_id, device_id)

    cmd = current_app.config['CMD_FACTORY'].get_read_command({
        _s_.BOARD_ID: board_id,
        _s_.DEVICE_ID: device_id,
        _s_.DEVICE_TYPE: get_device_type_code(device_type.lower()),
        _s_.DEVICE_TYPE_STRING: device_type.lower()
    })

    device = get_device_instance(board_id)
    response = device.handle(cmd)

    return jsonify(response.data)


@core.route(url('/power/<rack_id>/<board_id>/<device_id>/<power_action>'), methods=['GET'])
@core.route(url('/power/<device_type>/<rack_id>/<board_id>/<device_id>/<power_action>'), methods=['GET'])
@core.route(url('/power/<rack_id>/<board_id>/<device_id>'), methods=['GET'])
def power_control(power_action='status', rack_id=None, board_id=None, device_id=None, device_type='power'):
    """ Power on/off/cycle/status for the given board and port and device.

    Args:
        power_action (str): may be on/off/cycle/status and corresponds to the
            action to take.
        rack_id (str): the id of the rack which contains the board to accept
            the power control command
        board_id (str): the id of the board which contains the device that
            accepts power control commands.
        device_id (str): the id of the device which accepts power control
            commands.
        device_type (str): the type of device to accept power control command for.

    Returns:
        Power status of the given device.

    Raises:
        Returns a 500 error if the power command fails.
    """
    board_id, device_id = check_valid_board_and_device(board_id, device_id)

    if rack_id.lower() in [_s_.PWR_ON, _s_.PWR_OFF, _s_.PWR_CYCLE, _s_.PWR_STATUS]:
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

    return jsonify(response.data)


@core.route(url('/asset/<rack_id>/<board_id>/<device_id>'), methods=['GET'])
def asset_info(rack_id, board_id, device_id):
    """ Get asset information for a given board and device.

    Args:
        rack_id: The id of the rack where the target board resides
        board_id: The board number to get asset information for.
        device_id: The device number to get asset information for (must be system).

    Returns:
        Asset information about the given device.
    """
    board_id, device_id = check_valid_board_and_device(board_id, device_id)

    cmd = current_app.config['CMD_FACTORY'].get_asset_command({
        _s_.BOARD_ID: board_id,
        _s_.DEVICE_ID: device_id,
        _s_.DEVICE_TYPE: get_device_type_code(const.DEVICE_SYSTEM),
    })

    device = get_device_instance(board_id)
    response = device.handle(cmd)

    return jsonify(response.data)


@core.route(url('/boot_target/<rack_id>/<board_id>/<device_id>/<target>'), methods=['GET'])
@core.route(url('/boot_target/<rack_id>/<board_id>/<device_id>'), methods=['GET'])
def boot_target(rack_id, board_id, device_id, target=None):
    """ Get or set boot target for a given board and device.

    Args:
        rack_id: The id of the rack where the target board resides
        board_id: The board number to get/set boot target for.
        device_id: The device number to get/set boot target for (must be system).
        target: The boot target to choose, or, if None, just get info.

    Returns:
        Boot target of the device.
    """
    board_id, device_id = check_valid_board_and_device(board_id, device_id)

    if target is not None and target not in [_s_.BT_PXE, _s_.BT_HDD, _s_.BT_NO_OVERRIDE]:
        logger.error('Boot Target: Invalid boot target specified: %s board_id: %s device_id: %s', target, board_id,
                     device_id)
        raise OpenDCREException('Invalid boot target specified.')

    cmd = current_app.config['CMD_FACTORY'].get_boot_target_command({
        _s_.BOARD_ID: board_id,
        _s_.DEVICE_ID: device_id,
        _s_.DEVICE_TYPE: get_device_type_code(const.DEVICE_SYSTEM),
        _s_.BOOT_TARGET: target if target is not None else 'status'
    })

    device = get_device_instance(board_id)
    response = device.handle(cmd)

    return jsonify(response.data)


@core.route(url('/location/<rack_id>/<board_id>/<device_id>'), methods=['GET'])
@core.route(url('/location/<rack_id>/<board_id>'), methods=['GET'])
def device_location(rack_id, board_id=None, device_id=None):
    """ Get location of a device via PLC.  IPMI not supported, so unknown is returned.

    Args:
        rack_id: The id of the rack where the target board resides
        board_id: The board number to get location for.  IPMI boards not supported.
        device_id: The device number to get location for.  IPMI devices not supported.

    Returns: Location of device.

    """
    if device_id is not None:
        (board_id, device_id) = check_valid_board_and_device(board_id, device_id)
        if device_id > 0xFFFF:
            raise OpenDCREException('Device number must be <= 0xFFFF')
    else:
        board_id = check_valid_board(board_id)

    try:
        # add validation on the board by finding its device instance
        # if this is not a valid board, we raise an exception, as there is no valid location for it
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
        return jsonify({
            _s_.PHYSICAL_LOC: physical_location,
            _s_.CHASSIS_LOC: get_chassis_location(device_id)
        })
    else:
        return jsonify({
            _s_.PHYSICAL_LOC: physical_location
        })


def _chamber_led_control(board_id, device_id, led_state, rack_id, led_color, blink_state):
    """ Control chamber LED via PLC.

    Args:
        board_id: The board number of the LED controler for vapor_led.
        device_id: The device number of the LED controller for vapor_led.
        led_state: The state to set the specified LED to (on, off, no_override)
        rack_id: The ID of the rack whose LED segment is to be controlled (MIN_RACK_ID..MAX_RACK_ID)
        led_color: The RGB hex value of the color to set the LED to, or 'no_override'.
        blink_state: The blink state of the LED (blink, steady, no_override).
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

    return jsonify(response.data)


@core.route(url('/led/<rack_id>/<board_id>/<device_id>'), methods=['GET'])
@core.route(url('/led/<rack_id>/<board_id>/<device_id>/<led_state>'), methods=['GET'])
@core.route(url('/led/<rack_id>/<board_id>/<device_id>/<led_state>/<led_color>/<blink_state>'), methods=['GET'])
def led_control(rack_id, board_id, device_id, led_state=None, led_color=None, blink_state=None):
    """ Control LED on system or wedge rack.  System led may only be turned on/off. Wedge rack supports color

    Args:
        rack_id: The rack id to control led for.
        board_id: The board number to control led for. IPMI boards only support on/off.
        device_id: The device number to control led for. IPMI devices only support on/off.
        led_state: The state to set LED to (on/off for IPMI, on/off/blink for PLC).
        led_color: The hex RGB color to set LED to (for PLC wedge LED only).
        blink_state: The blink state (blink|steady|no_override) for PLC wedge LED only.

    Returns:
        LED state for chassis LED; LED state, color and blink state for PLC wedge LED.
    """
    board_id, device_id = check_valid_board_and_device(board_id, device_id)

    if led_state not in [_s_.LED_ON, _s_.LED_OFF, _s_.LED_NO_OVERRIDE, None]:
        logger.error('Invalid LED state {} provided for LED control.'.format(led_state))
        raise OpenDCREException('Invalid LED state provided for LED control.')

    if led_color is not None and led_color != _s_.LED_NO_OVERRIDE:
        try:
            led_color_int = int(led_color, 16)
            if (led_color_int < 0x000000) or (led_color_int > 0xffffff):
                raise ValueError('LED Color must be between 0x000000 and 0xffffff.')
        except ValueError as e:
            raise OpenDCREException('Invalid LED color specified. ({})'.format(e.message))

    if blink_state is not None and blink_state not in [_s_.LED_BLINK, _s_.LED_STEADY, _s_.LED_NO_OVERRIDE]:
        raise OpenDCREException('Invalid blink state specified for LED.')

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

    return jsonify(response.data)


@core.route(url('/fan/<rack_id>/<board_id>/<device_id>'), methods=['GET'])
@core.route(url('/fan/<rack_id>/<board_id>/<device_id>/<fan_speed>'), methods=['GET'])
def fan_control(rack_id, board_id, device_id, fan_speed=None):
    """ Control fan on system or Vapor Chamber.  System fan may only be polled for status
    unless explicitly supported.

    Args:
        rack_id: The rack id to control fan for.
        board_id: The board number to control fan for.
        device_id: The device number to control fan for.
        fan_speed: The speed to set fan to.

    Returns:
        fan speed in rpms
    """
    board_id, device_id = check_valid_board_and_device(board_id, device_id)

    # if we are reading the fan speed only, forward on to the device_read method and pass along response
    if fan_speed is None:
        return read_device(rack_id, const.DEVICE_FAN_SPEED, board_id, device_id)

    # convert fan speed to int
    if fan_speed is not None:
        try:
            fan_speed_int = int(fan_speed)
            # FIXME: we can move this to individual device instances which will give us finer-toothed control
            if definitions.MAX_FAN_SPEED < fan_speed_int or definitions.MIN_FAN_SPEED > fan_speed_int:
                raise ValueError('Fan speed out of acceptable range.')
        except ValueError as e:
            logger.error('Location: Error converting fan_speed: %s', str(fan_speed))
            raise OpenDCREException('Error converting fan_speed to integer ({}).'.format(e))

    cmd = current_app.config['CMD_FACTORY'].get_fan_command({
        _s_.BOARD_ID: board_id,
        _s_.DEVICE_ID: device_id,
        _s_.DEVICE_TYPE: get_device_type_code(const.DEVICE_FAN_SPEED),
        _s_.DEVICE_NAME: const.DEVICE_FAN_SPEED,
        _s_.FAN_SPEED: fan_speed
    })

    device = get_device_instance(board_id)
    response = device.handle(cmd)

    return jsonify(response.data)


@core.route(url('/host_info/<rack_id>/<board_id>/<device_id>'), methods=['GET'])
def host_info(rack_id, board_id, device_id):
    """ Get hostname and ip address for a given host (of type 'system'.  This uses
    the PLC TTY to login to the server, and retrieve the hostname[s] and ip address[es]

    Args:
        rack_id: The id of the rack where the target board resides
        board_id: The board number to get host info for.
        device_id: The device number to get host info for.

    Returns:
        hostname(s) and IP address(es)
    """
    board_id, device_id = check_valid_board_and_device(board_id, device_id)

    cmd = current_app.config['CMD_FACTORY'].get_host_info_command({
        _s_.BOARD_ID: board_id,
        _s_.DEVICE_ID: device_id,
        _s_.DEVICE_TYPE: get_device_type_code(const.DEVICE_SYSTEM),
        _s_.DEVICE_NAME: const.DEVICE_SYSTEM
    })

    device = get_device_instance(board_id)
    response = device.handle(cmd)

    return jsonify(response.data)
