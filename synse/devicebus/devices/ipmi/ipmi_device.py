#!/usr/bin/env python
""" Synse IPMI Device.

    Author: Erick Daniszewski
    Date:   09/15/2016

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

import json
import logging
import os
import sys
import threading

from pyghmi.exceptions import *

import synse.strings as _s_
from synse import constants as const
from synse.definitions import BMC_PORT
from synse.devicebus.constants import CommandId as cid
from synse.devicebus.devices.ipmi import vapor_ipmi
from synse.devicebus.devices.lan_device import LANDevice
from synse.devicebus.response import Response
from synse.errors import SynseException
from synse.utils import ThreadPool, get_measure_for_device_type
from synse.version import __api_version__, __version__

logger = logging.getLogger(__name__)


class IPMIDevice(LANDevice):
    """ Devicebus Interface for IPMI-routed commands.
    """
    _instance_name = 'ipmi'

    def __init__(self, app_cfg, counter, **kwargs):
        super(IPMIDevice, self).__init__()

        self._app_cfg = app_cfg
        self._count = counter

        # these are required, so if they are missing from the config
        # dict passed in, we will want the exception to propagate up
        self.bmc_ip = kwargs['bmc_ip']
        self.bmc_rack = kwargs['bmc_rack']
        self.username = kwargs['username']
        self.password = kwargs['password']

        # these are optional values, so they may not exist in the config.
        self.bmc_port = kwargs.get('bmc_port', BMC_PORT)  # 623 default port for ipmi
        # FIXME (etd): should the bmc_ip go in the hostnames field? its not a hostname
        #   and is already exposed via 'ip_addresses'
        # TODO: put dcmi hostname here if applicable
        self.hostnames = kwargs.get('hostnames', [self.bmc_ip])
        self.ip_addresses = kwargs.get('ip_addresses', [self.bmc_ip])
        self.scan_on_init = kwargs.get('scan_on_init', True)

        # bundle up the common IPMI args for easier command initialization
        self._ipmi_kwargs = {
            'username': self.username,
            'password': self.password,
            'ip_address': self.bmc_ip,
            'port': self.bmc_port
        }

        # override the command map to defines which commands are supported by IPMI.
        self._command_map = {
            cid.VERSION: self._version,
            cid.SCAN: self._scan,
            cid.SCAN_ALL: self._scan_all,
            cid.READ: self._read,
            cid.POWER: self._power,
            cid.ASSET: self._asset,
            cid.BOOT_TARGET: self._boot_target,
            cid.LED: self._led,
            cid.FAN: self._fan,
            cid.HOST_INFO: self._host_info
        }

        self.board_record = None
        self.board_id = None

        # if a scan cache file exists in the container, we will want to try and use that before
        # we assign a board id.
        # TODO: since board ids are sequential, we will want to move the 'next' sequence number to
        #   that of 1 + max(scan_board_ids)?

        if os.path.exists(self._app_cfg['SCAN_CACHE']):
            logger.debug('Scan cache exists -- attempting to initialize device off cache.')
            with open(self._app_cfg['SCAN_CACHE'], 'r') as f:
                scan_cache = json.load(f)

            # attempt to complete initialization using the cache. if this succeeds, the board id
            # and the board record will be updated (will no longer be None). if neither were
            # updated, we will initialize the board through 'normal' means next.
            self._load_from_cache(scan_cache)

        # assign board_id based on incoming data
        if self.board_id is None:
            self.board_id = int(kwargs['board_offset']) + int(kwargs['board_id_range'][0])

        if self.scan_on_init and self.board_record is None:
            self.board_record = self._get_board_record()

        if self.board_record is not None:
            # get FRU information for use in determining OEM support
            self.fru_info = self._get_fru_info()
            self.dcmi_supported = self._get_dcmi_power_capabilities()

    def __str__(self):
        return '<IPMIDevice (bmc: {}, rack: {})>'.format(self.bmc_ip, self.bmc_rack)

    def __repr__(self):
        return self.__str__()

    def _load_from_cache(self, scan_cache):
        """ Attempt to load in IPMIDevice state from the scan cache.

        Note that this should only be called from the `__init__` method as it is
        an alternative way to complete device initialization.

        Args:
            scan_cache (dict): the dictionary representing the scan cache file.
        """
        if 'racks' in scan_cache:
            for rack in scan_cache['racks']:
                rack_id = rack.get('rack_id')

                # the rack ids match -- this scan result belongs with this IPMI device instance
                if self.bmc_rack == rack_id:
                    # next, we get the associated board info for this IPMIDevice. the assumption
                    # here is that because a previous scan would operate on a previous IPMIDevice,
                    # and since IPMIDevice either uses its existing ip_addresses list (which should
                    # be a unique identifier) or adds its bmc_ip to the ip_addresses list, we can
                    # determine which board belongs to this device based on that information.
                    for board in rack.get('boards', []):
                        if self.ip_addresses == board['ip_addresses']:
                            # this is our board!
                            self.board_id = int(board['board_id'], 16)

                            # if 'device_interface' is listed in the scan cache, we want to ignore
                            # that. the device_interface is UUIDs mapped to the interface, which
                            # would not be the same if reloading. a new UUID will be generated for
                            # this interface later.
                            if 'device_interface' in board:
                                del board['device_interface']

                            self.board_record = board
                            logger.debug('Successfully loaded device state from scan cache.')
                            return

        logger.debug(
            'Failed to load device from scan cache - will continue initializing normally.')

        # if we get here, this IPMI device is not in the scan cache. this means we will
        # need to scan it "normally". for this, we need not do anything, as the logic in
        # the class initializer will do so if required.

    def duplicate_config(self, other):
        """ Check to see whether an IPMI config has the same values as this IPMI device.

        This is primarily used in determining whether or not to add a new device to
        the application. In cases where there is a match, we do not want to add a new
        device to prevent duplicate devices.

        Args:
            other (dict): dictionary representing an IPMI device config.

        Returns:
            bool: True if duplicate; False otherwise.
        """
        # FIXME (etd): could become __eq__
        return \
            self.bmc_ip == other.get('bmc_ip') and \
            self.bmc_rack == other.get('bmc_rack') and \
            self.username == other.get('username') and \
            self.password == other.get('password') and \
            self.bmc_port == other.get('bmc_port', BMC_PORT) and \
            self.hostnames == other.get('hostnames', [other['bmc_ip']]) and \
            self.ip_addresses == other.get('ip_addresses', [other['bmc_ip']])

    def _get_dcmi_power_capabilities(self):
        """ Get DCMI capabilities relative to power management (is the power management
        platform capability supported?)

        Returns:
            bool: True if 'DCMI Get Power Reading' is presumably supported, False
                otherwise. If an error is raised, this command returns False.
        """
        try:
            # 0x01 is the parameter selector for the general capabilities, which includes
            # power management
            return vapor_ipmi.get_dcmi_capabilities(
                parameter_selector=0x01, **self._ipmi_kwargs)['power_management']
        except:
            return False

    def _get_fru_info(self):
        """ Get FRU information for the given BMC (if possible).

        Returns:
            dict: the FRU information that is typically returned by the get_inventory
                IPMI method, or None if there is an error.
        """
        try:
            return vapor_ipmi.get_inventory(**self._ipmi_kwargs)
        except Exception, e:
            logger.warning(
                'Error retrieving inventory at startup scan for BMC '
                '({}) : {}'.format(self.bmc_ip, e))
            return None

    def _get_board_record(self):
        """ Get available sensors via IPMI and generate a board record with that data.

        Returns:
            dict: a dictionary containing the board's devices.
        """
        logger.debug('Getting board record for {}'.format(self.bmc_ip))

        board_record = dict()
        board_record['board_id'] = format(self.board_id, '08x')

        # TODO: add one more check on hostnames, by getting the host ID from DCMI (#303)
        board_record['hostnames'] = self.hostnames
        board_record['ip_addresses'] = self.ip_addresses

        # TODO: #306 - potentially collapse the static devices into a single system device
        board_record['devices'] = [
            {'device_id': '0100', 'device_type': 'power', 'device_info': 'power'},
            {'device_id': '0200', 'device_type': 'system', 'device_info': 'system'},
            {'device_id': '0300', 'device_type': 'led', 'device_info': 'led'}
        ]
        sensors = dict()

        try:
            sensors = vapor_ipmi.sensors(**self._ipmi_kwargs)
        except (SynseException, IpmiException, NotImplementedError) as e:
            logger.error('Unable to retrieve sensors for BMC: {} ({})'.format(
                self.bmc_ip, e.message))
            board_record = None
        except ValueError:
            logger.error('Invalid string in configuration for BMC: {}'.format(self.bmc_ip))
            board_record = None

        for sensor in sensors:
            sensor_type = sensor['sensor_type'].lower()
            if sensor_type in ['temperature', 'fan', 'voltage', 'power supply']:
                if sensor_type == 'fan':
                    # special case to map to our sensor type for fan speed
                    sensor_type = const.DEVICE_FAN_SPEED
                elif sensor_type == 'power supply':
                    sensor_type = const.DEVICE_POWER_SUPPLY

                board_record['devices'].append(
                    {
                        'device_id': format(sensor['sensor_number'], '04x'),
                        'device_type': sensor_type,
                        'device_info': sensor['id_string']
                    }
                )
            else:
                logger.warning('Sensor type "{}" is not supported.. skipping over.'.format(
                    sensor_type))

        return board_record

    @classmethod
    def register(cls, devicebus_config, app_config, app_cache):
        """ Register IPMI devices.

        Args:
            devicebus_config (dict): a dictionary containing the devicebus configurations
                for IPMI. within this dict is a list or reference to the actual configs
                for the IPMI devices themselves.
            app_config (dict): Flask application config, where application-wide
                configurations and constants are stored.
            app_cache (tuple): a tuple which contains the mutable structures
                which make up the app's device cache and lookup tables. The first
                item is a mapping of UUIDs to the devices registered here. The second
                item is a collection of "single board devices". All collections are
                mutated by this method to add all devices which are successfully
                registered, making them available to the Flask app.
        """
        cls.validate_app_state(app_cache)
        device_cache, single_board_devices = app_cache

        device_config = cls.get_device_config(devicebus_config)
        if not device_config:
            raise ValueError('Unable to get configuration for device - unable to register.')

        # define a thread lock so we can have synchronous mutations to the input
        # lists and dicts
        mutate_lock = threading.Lock()

        # FIXME - this is a pretty high level indicator and probably not too helpful
        # if attempting to debug (though one would expect the error to log out to file).
        # instead of just an indication of whether failure occurred or not, we may want
        # to surface where failure occurred.
        #
        # list to hold errors occurred during device initialization
        device_init_failure = []

        # get config associated with all IPMI devices
        thread_count = devicebus_config.get('device_initializer_threads', 1)
        scan_on_init = devicebus_config.get('scan_on_init', True)

        # create a thread pool which will be used for the lifetime of device registration
        thread_pool = ThreadPool(thread_count)

        # now, for each bmc, we create a device instance
        if 'racks' in device_config:
            for rack in device_config['racks']:
                rack_id = rack['rack_id']
                for bmc in rack['bmcs']:
                    # pass through scan on init value for all ipmi devices
                    bmc['scan_on_init'] = scan_on_init

                    # check to see if there are any duplicate BMCs already defined.
                    # this may be the case with the periodic registering of remote
                    # devices.
                    duplicates = False
                    if device_cache:
                        for dev in device_cache.values():
                            if isinstance(dev, IPMIDevice):
                                if dev.duplicate_config(bmc):
                                    duplicates = True
                                    break

                    if not duplicates:
                        thread_pool.add_task(
                            IPMIDevice._process_bmc, bmc, app_config, rack_id,
                            device_config.get('board_id_range', const.IPMI_BOARD_RANGE),
                            device_init_failure, mutate_lock, device_cache, single_board_devices
                        )

        # wait for all devices to be initialized
        thread_pool.wait_for_task_completion()

        # check for device initialization failures
        if device_init_failure:
            logger.error('Failed to initialize IPMI devices: {}'.format(device_init_failure))
            raise SynseException('Failed to initialize IPMI devices.')

    @staticmethod
    def _process_bmc(bmc, app_config, rack_id, board_range, device_init_failure, mutate_lock,
                     devices, single_board_devices):
        """ A private method to handle the construction of the IPMI device from
        the bmc record.

        Args:
            bmc: the record for the bmc, containing its configurations
            rack_id: the id of the rack which the bmc is a part of
            board_range: range of ids the board should fall within
            device_init_failure (list): list to track any failures in the
                registrar thread
            mutate_lock (Lock): threading lock used when mutating shared state
            devices (list[dict]): a list of dictionary configurations for the
                defined devices.
            single_board_devices (dict): collection of 'single board devices'
                tracked by the Flask application for convenience. this wil be
                mutated to add in the appropriate records from this method's
                device registration.
        """
        bmc['bmc_rack'] = rack_id
        bmc['board_offset'] = app_config['IPMI_BOARD_OFFSET'].next()
        bmc['board_id_range'] = board_range

        try:
            # generate a unique ID which will be used internally to reference the
            # device which will be created and mapped to racks/boards.
            ipmi_device = IPMIDevice(
                app_cfg=app_config,
                counter=app_config['COUNTER'],
                **bmc
            )
        except Exception as e:
            logger.error('Error initializing device: ')
            logger.exception(e)
            device_init_failure.append(e)
            raise

        # now, with the ipmi device initialized, we will need to update the app
        # state for the ipmi device.
        with mutate_lock:
            devices[ipmi_device.device_uuid] = ipmi_device

            # this is a device that owns a single board_id so it gets tucked into
            # _single_board_devices
            single_board_devices[ipmi_device.board_id] = ipmi_device

            # next, add hostname and ip address keying for friendly (non-board-id lookup)
            if ipmi_device.hostnames is not None:
                for hostname in ipmi_device.hostnames:
                    if hostname not in single_board_devices:
                        single_board_devices[hostname] = ipmi_device
                    else:
                        logger.info(
                            'Duplicate hostname ({}) found in BMC configuration - '
                            'skipping.'.format(hostname)
                        )

            if ipmi_device.ip_addresses is not None:
                for ip_address in ipmi_device.ip_addresses:
                    if ip_address not in single_board_devices:
                        single_board_devices[ip_address] = ipmi_device
                    else:
                        logger.info(
                            'Duplicate IP address ({}) found in BMC configuration - '
                            'skipping.'.format(ip_address)
                        )

    def _version(self, command):
        """ Get the version information for a given board.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the version response.
        """
        return Response(
            command=command,
            response_data={
                'api_version': __api_version__,
                'synse_version': __version__,
                'firmware_version': 'Synse IPMI Bridge v2.0'
            }
        )

    def _scan(self, command):
        """ Get the scan information for a given board.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the scan response.
        """
        boards = [] if self.board_record is None else [self.board_record]
        return Response(
            command=command,
            response_data={
                'boards': boards
            }
        )

    def _scan_all(self, command):
        """ Get the scan information from a 'broadcast' (e.g. scan all) command.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the scan all response.
        """
        # get the command data out from the incoming command
        force = command.data.get(_s_.FORCE, False)

        if force:
            self.board_record = self._get_board_record()

            if self.board_record is not None:
                # get FRU information for use in determining OEM support
                self.fru_info = self._get_fru_info()
                self.dcmi_supported = self._get_dcmi_power_capabilities()

        boards = [] if self.board_record is None else [self.board_record]
        scan_results = {'racks': [
            {
                'rack_id': self.bmc_rack,
                'boards': boards
            }
        ]}

        return Response(
            command=command,
            response_data=scan_results
        )

    def _read(self, command):
        """ Read the data off of a given board's device.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the read response.
        """
        # get the command data out from the incoming command
        device_id = command.data[_s_.DEVICE_ID]
        device_type_string = command.data[_s_.DEVICE_TYPE_STRING]

        try:
            device = self._get_device_by_id(device_id, device_type_string)

            reading = vapor_ipmi.read_sensor(sensor_name=device['device_info'],
                                             **self._ipmi_kwargs)
            response = dict()

            uom = get_measure_for_device_type(device['device_type'])
            if uom is not None:
                response[uom] = reading['sensor_reading']

            response['health'] = reading['health']
            response['states'] = reading['states']

            if response is not None:
                return Response(
                    command=command,
                    response_data=response
                )

            # if we get here, there was no sensor device found, so we must raise
            logger.error('No response for sensor reading for command: {}'.format(
                command.data))
            raise SynseException('No sensor reading returned from BMC.')

        except Exception:
            raise SynseException('Error reading IPMI sensor (device id: {})'.format(
                device_id)), None, sys.exc_info()[2]

    def _power(self, command):
        """ Power control command for a given board and device.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the power response.
        """
        # get the command data out from the incoming command
        device_id = command.data[_s_.DEVICE_ID]
        power_action = command.data[_s_.POWER_ACTION]

        try:
            if power_action not in [_s_.PWR_ON, _s_.PWR_OFF, _s_.PWR_CYCLE, _s_.PWR_STATUS]:
                raise ValueError('Invalid IPMI power action {} for board {} device {}.'.format(
                    power_action, self.board_id, device_id
                ))
            # determine if there are OEM considerations
            # for reading power
            reading_method = None

            if self.dcmi_supported:
                reading_method = 'dcmi'

            if self.fru_info is not None:
                if self.fru_info['board_info']['manufacturer'] == 'Ciii USA Inc':
                    # flex OEM support should override dcmi support
                    reading_method = 'flex-victoria'

            # validate device supports power control
            self._get_device_by_id(device_id, const.DEVICE_POWER)

            power_status = vapor_ipmi.power(cmd=power_action, reading_method=reading_method,
                                            **self._ipmi_kwargs)

            """
            NB(ABC): disabled this but it could be re-enabled - if the DCMI Power Reading
                command is giving trouble elsewhere, we could re-enable this, but the checks
                done at startup should obviate the need for this logic for now.
            # check reading method, and if 'dcmi' and input_power is 'unknown', set reading_method
            # to 'None' in the future; 'unknown' indicates an exception occurred, which we do not
            # wish to repeat
            if reading_method == 'dcmi' and power_status['input_power'] == 'uknown':
                self.dcmi_supported = False
            """

            if power_status is not None:
                return Response(
                    command=command,
                    response_data=power_status
                )

            # if we get here there is either no device found, or response received
            logger.error('Power control attempt returned no data: {}'.format(command.data))
            raise SynseException('No response from BMC for power control action.')

        except Exception:
            raise SynseException('Error for power control via IPMI (device id: {}).'.format(
                device_id)), None, sys.exc_info()[2]

    def _asset(self, command):
        """ Asset info command for a given board and device.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the asset response.
        """
        # get the command data out from the incoming command
        device_id = command.data[_s_.DEVICE_ID]

        try:
            # validate that asset is supported for the device
            self._get_device_by_id(device_id, const.DEVICE_SYSTEM)
            asset_data = vapor_ipmi.get_inventory(**self._ipmi_kwargs)
            asset_data['bmc_ip'] = self.bmc_ip

            if asset_data is not None:
                return Response(
                    command=command,
                    response_data=asset_data
                )

            logger.error('No response getting asset info for {}'.format(command.data))
            raise SynseException(
                'No response from BMC when retrieving asset information via IPMI.')

        except Exception:
            raise SynseException('Error getting IPMI asset info (device id: {})'.format(
                device_id)), None, sys.exc_info()[2]

    def _boot_target(self, command):
        """ Boot target command for a given board and device.

        If a boot target is specified, this will attempt to set the boot device.
        Otherwise, it will just retrieve the currently configured boot device.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the boot target response.
        """
        # get the command data out from the incoming command
        device_id = command.data[_s_.DEVICE_ID]
        boot_target = command.data[_s_.BOOT_TARGET]

        try:
            if boot_target is None or boot_target == 'status':
                self._get_device_by_id(device_id, const.DEVICE_SYSTEM)
                boot_info = vapor_ipmi.get_boot(**self._ipmi_kwargs)
            else:
                boot_target = _s_.BT_NO_OVERRIDE if boot_target not in [_s_.BT_PXE, _s_.BT_HDD] \
                    else boot_target
                self._get_device_by_id(device_id, const.DEVICE_SYSTEM)
                boot_info = vapor_ipmi.set_boot(target=boot_target, **self._ipmi_kwargs)

            if boot_info is not None:
                return Response(
                    command=command,
                    response_data=boot_info
                )

            logger.error('No response for boot target operation: {}'.format(command.data))
            raise SynseException('No response from BMC on boot target operation via IPMI.')

        except Exception:
            raise SynseException('Error getting or setting IPMI boot target '
                                 '(device id: {})'.format(device_id)), None, sys.exc_info()[2]

    def _led(self, command):
        """ LED command for a given board and device.

        If an LED state is specified, this will attempt to set the LED state
        of the given device. Otherwise, it will just retrieve the currently
        configured LED state.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the LED response.
        """
        # get the command data out from the incoming command
        device_id = command.data[_s_.DEVICE_ID]
        led_state = command.data[_s_.LED_STATE]

        try:
            if led_state is not None:
                self._get_device_by_id(device_id, const.DEVICE_LED)
                led_state = 0 if led_state.lower() == _s_.LED_OFF else 1
                led_response = vapor_ipmi.set_identify(led_state=led_state,
                                                       **self._ipmi_kwargs)
                led_response['led_state'] = _s_.LED_OFF if led_response['led_state'] == 0 \
                    else _s_.LED_ON
            else:
                self._get_device_by_id(device_id, const.DEVICE_LED)
                led_response = vapor_ipmi.get_identify(**self._ipmi_kwargs)

            if led_response is not None:
                return Response(
                    command=command,
                    response_data=led_response
                )

            logger.error('No response for LED control operation: {}'.format(command.data))
            raise SynseException('No response from BMC on LED operation via IPMI.')

        except Exception:
            raise SynseException('Error with LED control (device id: {})'.format(
                device_id)), None, sys.exc_info()[2]

    def _fan(self, command):
        """ Fan speed control command for a given board and device.

        Gets the fan speed for a given device. Since this is not NOT a Vapor
        Fan, we can not control the fan speed, so any attempts to set the
        fan speed are met with a SynseException being raised.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the fan response.
        """
        # get the command data out from the incoming command
        device_id = command.data[_s_.DEVICE_ID]
        device_name = command.data[_s_.DEVICE_NAME]
        fan_speed = command.data[_s_.FAN_SPEED]

        try:
            if fan_speed is not None:
                raise SynseException('Setting of fan speed is not permitted for this device.')
            else:
                device = self._get_device_by_id(device_id, const.DEVICE_FAN_SPEED)
                reading = vapor_ipmi.read_sensor(sensor_name=device_name, **self._ipmi_kwargs)
                response = dict()
                if device['device_type'] == const.DEVICE_FAN_SPEED:
                    response[const.UOM_FAN_SPEED] = reading['sensor_reading']
                else:
                    raise SynseException('Attempt to get fan speed for non-fan device.')

                response['health'] = reading['health']
                response['states'] = reading['states']

                if response is not None:
                    return Response(
                        command=command,
                        response_data=response
                    )

            logger.error('No response for fan control operation: {}'.format(command.data))
            raise SynseException('No response from BMC on fan operation via IPMI.')

        except Exception:
            raise SynseException('Error with fan control (device id: {})'.format(
                device_id)), None, sys.exc_info()[2]

    def _host_info(self, command):
        """ Get the host information for a given board.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the host info response.
        """
        return Response(
            command=command,
            response_data={
                'hostnames': self.hostnames,
                'ip_addresses': self.ip_addresses if self.ip_addresses else [self.bmc_ip]
            }
        )
