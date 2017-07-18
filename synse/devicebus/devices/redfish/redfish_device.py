#!/usr/bin/env python
""" Synse Redfish Device.

NOTE (v1.3): Redfish is still in Beta and is untested on live hardware.


    Author: Morgan Morley Mills
            Erick Daniszewski
    Date:   01/19/2017

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
import threading

import vapor_redfish
from redfish_connection import find_links

import synse.strings as _s_
from synse import constants as const
from synse.devicebus.constants import CommandId as cid
from synse.devicebus.devices.lan_device import LANDevice
from synse.devicebus.response import Response
from synse.errors import SynseException
from synse.utils import ThreadPool
from synse.version import __api_version__, __version__

logger = logging.getLogger(__name__)


class RedfishDevice(LANDevice):
    """ Devicebus Interface for Redfish-routed commands.
    """
    _instance_name = 'redfish'

    def __init__(self, app_cfg, counter, **kwargs):
        super(RedfishDevice, self).__init__()

        self._app_cfg = app_cfg
        self._count = counter

        # these are required, so if they are missing from the config
        # dict passed in, we will want the exception to propagate up
        self.redfish_ip = kwargs['redfish_ip']
        self.server_rack = kwargs['server_rack']
        self.username = kwargs['username']
        self.password = kwargs['password']
        self.redfish_port = kwargs['redfish_port']

        # these are optional values, so they may not exist in the config.
        self.timeout_sec = kwargs.get('timeout', 5)
        self.hostnames = kwargs.get('hostnames', [self.redfish_ip])
        self.ip_addresses = kwargs.get('ip_addresses', [self.redfish_ip])
        self.scan_on_init = kwargs.get('scan_on_init', True)
        # self.session_token = kwargs.get('session_token')

        # bundle up the Redfish auth args for easier command initialization
        self._redfish_request_kwargs = {
            'timeout': self.timeout_sec,
            'username': self.username,
            'password': self.password
        }

        # override the command map to defines which commands are supported
        # by Redfish.
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

        # stores links for use within the command functions
        self._redfish_links = find_links(
            self.redfish_ip, self.redfish_port, **self._redfish_request_kwargs)

        # assign board_id based on incoming data
        self.board_id = int(kwargs['board_offset']) + int(kwargs['board_id_range'][0])

        self.board_record = None
        if self.scan_on_init:
            self.board_record = self._get_board_record()

    def duplicate_config(self, other):
        """ Check to see whether an Redfish config has the same values as this Redfish
        device. This is primarily used in determining whether or not to add a new
        device to the application. In cases where there is a match, we do not want
        to add a new device to prevent duplicate devices.

        Args:
            other (dict): dictionary representing an Redfish device config.

        Returns:
            bool: True if duplicate; False otherwise.
        """
        # FIXME (etd) - this could become __eq__
        return \
            self.redfish_ip == other.get('redfish_ip') and \
            self.server_rack == other.get('server_rack') and \
            self.username == other.get('username') and \
            self.password == other.get('password') and \
            self.redfish_port == other.get('redfish_port') and \
            self.hostnames == other.get('hostnames', [other['redfish_ip']]) and \
            self.ip_addresses == other.get('ip_addresses', [other['redfish_ip']])  # and \
            # self.session_token == other.get('session_token')
            # TODO - for session capability, session tokens may be required.

    def _get_board_record(self):
        """ Get the board information and available sensors via Redfish.

        Returns:
            dict: dictionary containing board's devices.
        """
        board_record = dict()
        board_record['board_id'] = format(self.board_id, '08x')
        board_record['hostnames'] = self.hostnames
        board_record['ip_addresses'] = self.ip_addresses

        board_record['devices'] = [
            {'device_id': '0100', 'device_type': 'power', 'device_info': 'power'},
            {'device_id': '0200', 'device_type': 'system', 'device_info': 'system'},
            {'device_id': '0300', 'device_type': 'led', 'device_info': 'led'}
        ]

        links_list = [self._redfish_links['thermal'], self._redfish_links['power']]

        try:
            sensors = vapor_redfish.find_sensors(links=links_list, **self._redfish_request_kwargs)
            board_record['devices'].extend(sensors)
        except ValueError:
            logger.exception('Invalid string in configuration for Redfish: %s', self.redfish_ip)
            board_record = None

        return board_record

    @classmethod
    def register(cls, devicebus_config, app_config, app_cache):
        """ Register Redfish devices.

        Args:
            devicebus_config (dict): a dictionary containing the devicebus configurations
                for Redfish. within this dict is a list or reference to the actual configs
                for the Redfish devices themselves.
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

        # define a thread lock so we can have synchronous mutations to the input
        # lists and dicts
        mutate_lock = threading.Lock()

        # list to hold errors occurred during device initialization
        device_init_failure = []

        # get config associated with all Redfish devices
        thread_count = devicebus_config.get('device_initializer_threads', 1)
        scan_on_init = devicebus_config.get('scan_on_init', True)

        # create a thread pool which will be used for the lifetime of device registration
        thread_pool = ThreadPool(thread_count)

        # configuration defined in separate file
        if 'from_config' in devicebus_config:
            with open(devicebus_config['from_config']) as f:
                device_config = json.load(f)

        # configuration is defined inline of the current file
        elif 'config' in devicebus_config:
            device_config = devicebus_config['config']

        # otherwise, there is no valid device config specified
        else:
            raise ValueError(
                'No valid device config found for Redfish configuration. Requires either the '
                '"from_config" field or the "config" field.'
            )
        # now, for each Redfish server, we create a device instance
        if 'racks' in device_config:
            for rack in device_config['racks']:
                rack_id = rack['rack_id']
                for server in rack['servers']:
                    # pass through scan on init value for all Redfish devices
                    server['scan_on_init'] = scan_on_init

                    # check to see if there are any duplicate Redfish servers already defined.
                    # this may be the case with the periodic registering of remote
                    # devices.
                    if device_cache:
                        duplicates = False
                        for dev in device_cache.values():
                            if isinstance(dev, RedfishDevice):
                                if dev.duplicate_config(server):
                                    duplicates = True
                                    break

                        if not duplicates:
                            RedfishDevice._process_server(
                                server, app_config, rack_id,
                                device_config.get('board_id_range', const.REDFISH_BOARD_RANGE),
                                device_init_failure, mutate_lock, device_cache,
                                single_board_devices
                            )

                            # FIXME (etd)
                            #  a GIL issue appears to be causing the threaded _process_server
                            #  resolution to hang. this can likely be fixed by figuring out
                            #  what the GIL is deadlocking on (probably an import dependency?)
                            #  and updating Synse's caching component to import in the main
                            #  thread. Until then, its easier and faster to just disable
                            #  threading and do device registration serially.

                            # thread_pool.add_task(
                            #     RedfishDevice._process_server, server, app_config, rack_id,
                            #     device_config.get('board_id_range', const.REDFISH_BOARD_RANGE),
                            #     device_init_failure, mutate_lock, device_cache,
                            #     single_board_devices
                            # )

                    else:
                        RedfishDevice._process_server(
                            server, app_config, rack_id,
                            device_config.get('board_id_range', const.REDFISH_BOARD_RANGE),
                            device_init_failure, mutate_lock, device_cache, single_board_devices
                        )

                        # FIXME (etd)
                        #  a GIL issue appears to be causing the threaded _process_server
                        #  resolution to hang. this can likely be fixed by figuring out what
                        #  the GIL is deadlocking on (probably an import dependency?) and
                        #  updating Synse's caching component to import in the main thread.
                        #  Until then, its easier and faster to just disable threading and do
                        #  device registration serially.

                        # thread_pool.add_task(
                        #     RedfishDevice._process_server, server, app_config, rack_id,
                        #     device_config.get('board_id_range', const.REDFISH_BOARD_RANGE),
                        #     device_init_failure, mutate_lock, device_cache, single_board_devices
                        # )

        # wait for all devices to be initialized
        thread_pool.wait_for_task_completion()

        # check for device initialization failures
        if device_init_failure:
            logger.error('Failed to initialize Redfish devices: {}'.format(device_init_failure))
            raise SynseException('Failed to initialize Redfish devices.')

    @staticmethod
    def _process_server(server, app_config, rack_id, board_range, device_init_failure, mutate_lock,
                        devices, single_board_devices):
        """ A private method to handle the construction of the Redfish device from
        the Redfish server record.

        Args:
            server (dict): the record for the Redfish server, containing its configurations.
            rack_id (str): the id of the rack which the Redfish server is on.
            board_range (tuple): range of ids the board should fall within.
            device_init_failure (list): list to track any failures in the
                registrar thread.
            mutate_lock (Lock): threading lock used when mutating shared state.
            devices (list[dict]): a list of dictionary configurations for the
                defined devices.
            single_board_devices (dict): collection of "single board devices"
                tracked by the Flask application for convenience. this wil be
                mutated to add in the appropriate records from this method's
                device registration.
        """
        server['server_rack'] = rack_id
        server['board_offset'] = app_config['REDFISH_BOARD_OFFSET'].next()
        server['board_id_range'] = board_range

        try:
            # generate a unique ID which will be used internally to reference the
            # device which will be created and mapped to racks/boards.
            redfish_device = RedfishDevice(
                app_cfg=app_config,
                counter=app_config['COUNTER'],
                **server
            )
        except Exception as e:
            logger.error('Error initializing device: ')
            logger.exception(e)
            device_init_failure.append(e)
            raise

        # now, with the Redfish device initialized, we will need to update the app
        # state for the Redfish device.
        with mutate_lock:
            devices[redfish_device.device_uuid] = redfish_device

            # this is a device that owns a single board_id so it gets tucked into
            # _single_board_devices
            single_board_devices[redfish_device.board_id] = redfish_device

            # next, add hostname and ip address keying for friendly (non-board-id lookup)
            if redfish_device.hostnames is not None:
                for hostname in redfish_device.hostnames:
                    if hostname not in single_board_devices:
                        single_board_devices[hostname] = redfish_device
                    else:
                        logger.info(
                            'Duplicate hostname ({}) found in Redfish configuration - '
                            'skipping.'.format(hostname)
                        )

            if redfish_device.ip_addresses is not None:
                for ip_address in redfish_device.ip_addresses:
                    if ip_address not in single_board_devices:
                        single_board_devices[ip_address] = redfish_device
                    else:
                        logger.info(
                            'Duplicate IP address ({}) found in Redfish configuration - '
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
                'firmware_version': 'Synse Redfish Bridge v1.0'
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
            self._redfish_links = find_links(self.redfish_ip, self.redfish_port,
                                             **self._redfish_request_kwargs)
            self.board_record = self._get_board_record()

        boards = [] if self.board_record is None else [self.board_record]
        scan_results = {'racks': [
            {
                'rack_id': self.server_rack,
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
        response = dict()

        _device_type_string = device_type_string.lower()

        if _device_type_string == const.DEVICE_FAN_SPEED:
            device_type = 'Fans'
        elif _device_type_string == const.DEVICE_TEMPERATURE:
            device_type = 'Temperatures'
        elif _device_type_string == const.DEVICE_VOLTAGE:
            device_type = 'Voltages'
        elif _device_type_string == const.DEVICE_POWER_SUPPLY:
            device_type = 'PowerSupplies'
        else:
            logger.error('Unsupported device type for Redfish device: {}'.format(
                device_type_string))
            raise SynseException('{} not a supported device type for Redfish.'.format(
                device_type_string))

        try:
            # check if the device raises an exception
            device = self._get_device_by_id(device_id, device_type_string)
            device_name = device['device_info']

            if _device_type_string in [const.DEVICE_FAN_SPEED, const.DEVICE_TEMPERATURE]:
                links_list = [self._redfish_links['thermal']]
                response = vapor_redfish.get_thermal_sensor(
                    device_type=device_type,
                    device_name=device_name,
                    links=links_list,
                    **self._redfish_request_kwargs
                )
            elif _device_type_string in [const.DEVICE_VOLTAGE, const.DEVICE_POWER_SUPPLY]:
                links_list = [self._redfish_links['power']]
                response = vapor_redfish.get_power_sensor(
                    device_type=device_type,
                    device_name=device_name,
                    links=links_list,
                    **self._redfish_request_kwargs
                )

            if response:
                return Response(
                    command=command,
                    response_data=response
                )

            # if we get here, there was no sensor device found, so we must raise
            logger.error('No response for sensor reading for command: {}'.format(command.data))
            raise SynseException('No sensor reading returned from Redfish server.')
        except ValueError as e:
            logger.error('Error reading Redfish sensor: {}'.format(e.message))
            logger.exception(e)
            raise SynseException('Error reading Redfish sensor: {}'.format(e.message))

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
            # validate device supports power control
            self._get_device_by_id(device_id, const.DEVICE_POWER)

            if power_action not in [_s_.PWR_ON, _s_.PWR_OFF, _s_.PWR_CYCLE, _s_.PWR_STATUS]:
                raise ValueError(
                    'Invalid Redfish power action {} for board {} device {}.'.format(
                        power_action, self.board_id, device_id)
                )
            else:
                links_list = [self._redfish_links['system'], self._redfish_links['power']]
                if power_action == 'status':
                    response = vapor_redfish.get_power(links=links_list,
                                                       **self._redfish_request_kwargs)
                else:
                    response = vapor_redfish.set_power(power_action, links=links_list,
                                                       **self._redfish_request_kwargs)

            if response:
                return Response(
                    command=command,
                    response_data=response
                )

            # if we get here there is either no device found, or response received
            logger.error('Power control attempt returned no data: {}'.format(command.data))
            raise SynseException('No response from Redfish server for power control action.')

        except ValueError as e:
            logger.error('Error controlling Redfish power: {}'.format(command.data))
            raise SynseException(
                'Error returned from Redfish server in controlling power '
                'via Redfish ({}).'.format(e)
            )

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

            links_list = [self._redfish_links['chassis'], self._redfish_links['system'],
                          self._redfish_links['bmc']]

            response = vapor_redfish.get_asset(links=links_list,
                                               **self._redfish_request_kwargs)
            response['redfish_ip'] = self.redfish_ip

            if 'chassis_info' in response:
                return Response(
                    command=command,
                    response_data=response
                )

            logger.error('No response getting asset info for {}'.format(command.data))
            raise SynseException('No response from Redfish server when retrieving asset '
                                 'information via Redfish.')
        except ValueError as e:
            logger.error('Error getting Redfish asset info: {}'.format(command.data))
            raise SynseException(
                'Error returned from Redfish server when retrieving asset info '
                'via Redfish ({}).'.format(e)
            )

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
            # check if the device raises an exception
            self._get_device_by_id(device_id, const.DEVICE_SYSTEM)

            links_list = [self._redfish_links['system']]

            if boot_target in [None, 'status']:
                response = vapor_redfish.get_boot(links=links_list,
                                                  **self._redfish_request_kwargs)
            else:
                boot_target = _s_.BT_NO_OVERRIDE if boot_target not in [_s_.BT_PXE, _s_.BT_HDD] else boot_target
                response = vapor_redfish.set_boot(target=boot_target, links=links_list, **self._redfish_request_kwargs)

            if response:
                return Response(
                    command=command,
                    response_data=response
                )

            logger.error('No response for boot target operation: {}'.format(command.data))
            raise SynseException('No response from Redfish server on boot target operation via Redfish.')

        except ValueError as e:
            logger.error('Error getting or setting Redfish boot target: {}'.format(command.data))
            raise SynseException(
                'Error returned from Redfish server during boot target operation via Redfish ({}).'.format(e)
            )

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
        # get the command data from the incoming command:
        device_id = command.data[_s_.DEVICE_ID]
        led_state = command.data[_s_.LED_STATE]

        try:
            # check if the device raises an exception
            self._get_device_by_id(device_id, const.DEVICE_LED)

            links_list = [self._redfish_links['chassis']]

            if led_state is not None and led_state.lower() != _s_.LED_NO_OVERRIDE:
                if led_state.lower() in [_s_.LED_ON, _s_.LED_OFF]:
                    led_state = 'Off' if led_state.lower() == _s_.LED_OFF else 'Lit'
                    response = vapor_redfish.set_led(led_state=led_state, links=links_list, **self._redfish_request_kwargs)
                else:
                    logger.error('LED state unsupported for LED control operation: {}'.format(led_state))
                    raise SynseException('Unsupported state change to Redfish server on LED operation.')
            else:
                response = vapor_redfish.get_led(links=links_list, **self._redfish_request_kwargs)

            if response:
                return Response(
                    command=command,
                    response_data=response
                )

            logger.error('No response for LED control operation: {}'.format(command.data))
            raise SynseException('No response from Redfish server on LED operation.')

        except ValueError as e:
            logger.error('Error with LED control: {}'.format(command.data))
            raise SynseException(
                'Error returned from Redfish server during LED operation via Redfish ({}).'.format(e)
            )

    def _fan(self, command):
        """ Fan speed control command for a given board and device.

        Gets the fan speed for a given device. Since this is not NOT a Vapor
        Fan we can not control the fan speed, so any attempts to set the
        fan speed are met with a SynseException being raised.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the fan response.
        """
        device_id = command.data[_s_.DEVICE_ID]
        device_name = command.data[_s_.DEVICE_NAME]
        fan_speed = command.data[_s_.FAN_SPEED]

        try:
            if fan_speed is not None:
                raise SynseException('Setting of fan speed is not permitted for this device.')

            else:
                # check if the device raises an exception
                device = self._get_device_by_id(device_id, const.DEVICE_FAN_SPEED)
                if device['device_type'] != const.DEVICE_FAN_SPEED:
                    raise SynseException('Attempt to get fan speed for non-fan device.')

                links_list = [self._redfish_links['thermal']]

                response = vapor_redfish.get_thermal_sensor(
                    device_type='Fans',
                    device_name=device_name,
                    links=links_list,
                    **self._redfish_request_kwargs
                )

                if response:
                    return Response(
                        command=command,
                        response_data=response
                    )

            logger.error('No response for fan control operation: {}'.format(command.data))
            raise SynseException('No response from Redfish server on fan operation via Redfish.')

        except ValueError as e:
            logger.error('Error with fan control: {}'.format(command.data))
            raise SynseException(
                'Error returned from Redfish server during fan operation via Redfish ({}).'.format(e)
            )

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
                'ip_addresses': self.ip_addresses if self.ip_addresses else [self.redfish_ip]
            }
        )
