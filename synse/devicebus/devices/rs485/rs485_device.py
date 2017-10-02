#!/usr/bin/env python
""" Synse RS485 Device.

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

import logging

import json
import lockfile
import os
import serial
import string
import requests

from synse import constants as const
from synse.devicebus.constants import CommandId as cid
from synse.devicebus.devices.serial_device import SerialDevice
from synse.devicebus.response import Response
from synse.errors import SynseException
from synse.protocols.modbus import dkmodbus
from synse.vapor_common import http
from synse.version import __api_version__, __version__
from urlparse import urlparse

logger = logging.getLogger(__name__)


class RS485Device(SerialDevice):
    """ Base class for all RS485 device implementations.
    """
    HARDWARE_TYPE_UNKNOWN = 'Unknown hardware type {}.'
    proto = 'rs485'

    def __init__(self, **kwargs):
        super(RS485Device, self).__init__(lock_path=kwargs['lockfile'])

        self._set_hardware_type(kwargs.get('hardware_type', 'unknown'))

        self.device_name = kwargs['device_name']

        # The emulators are defaulting to 19200, None.
        # For real hardware it's a good idea to configure this.
        self.baud_rate = kwargs.get('baud_rate', 19200)
        self.parity = kwargs.get('parity', 'N')
        self.rack_id = kwargs['rack_id']
        self.unit = kwargs['device_unit']

        self.timeout = kwargs.get('timeout', 0.15)
        self.method = kwargs.get('method', 'rtu')

        self._lock = lockfile.LockFile(self.serial_lock)

        # the device is read from a background process
        self.from_background = kwargs.get('from_background', False)

        # Common RS-485 commands.
        self._command_map = {
            cid.SCAN: self._scan,
            cid.SCAN_ALL: self._scan_all,
            cid.VERSION: self._version,
        }

    def __str__(self):
        return '<{} (rack: {}, board: {:08x})>'.format(
            self.__class__.__name__, self.rack_id, self.board_id)

    def __repr__(self):
        return self.__str__()

    @classmethod
    def register(cls, devicebus_config, app_config, app_cache):
        """ Register RS485 devices.

        Args:
            devicebus_config (dict): a dictionary containing the devicebus configurations
                for RS485. within this dict is a list or reference to the actual configs
                for the RS485 devices themselves.
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

        # now, for each device in rs485 devices, we create a device instance
        if 'racks' in device_config:
            for rack in device_config['racks']:
                for rs485_device in rack['devices']:
                    rs485_device['rack_id'] = rack['rack_id']
                    rs485_device['board_offset'] = app_config['RS485_BOARD_OFFSET'].next()
                    rs485_device['board_id_range'] = device_config.get('board_id_range',
                                                                       const.RS485_BOARD_RANGE)
                    rs485_device['hardware_type'] = rack.get('hardware_type', 'unknown')
                    rs485_device['device_name'] = rack['device_name']
                    rs485_device['lockfile'] = rack['lockfile']

                    # check whether the device is controlled by a background process
                    # or if directly by the synse app.
                    rs485_device['from_background'] = rack.get('from_background', False)

                    # since we are unable to import subclasses (circular import), but
                    # we still need to initialize a subclassed device interface, we
                    # match the configured 'device_model' with the '_instance_name' of
                    # all subclasses to determine the correct subclass at runtime.
                    device_model = {
                        klass._instance_name: klass for klass in cls.__subclasses__()
                    }.get(rs485_device['device_model'].lower())

                    if device_model:
                        try:
                            device_instance = device_model(**rs485_device)
                        except Exception as e:
                            logger.error('Error initializing device: ')
                            logger.exception(e)
                            raise

                        # cache reference to device
                        device_cache[device_instance.device_uuid] = device_instance
                        single_board_devices[device_instance.board_id] = device_instance
                    else:
                        logger.warning(
                            'Unsupported device model ({}) found. Skipping registration.'.format(
                                rs485_device['device_model'])
                        )

        else:
            logger.warning('Device configuration should specify "racks"!')

    def _scan(self, command):
        """ Common scan functionality for all RS-485 devices.

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
        """ Common scan all functionality for all RS-485 devices.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the scan all response.
        """
        boards = [] if self.board_record is None else [self.board_record]
        scan_results = {'racks': [
            {
                'rack_id': self.rack_id,
                'boards': boards
            }
        ]}

        return Response(
            command=command,
            response_data=scan_results
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
                'firmware_version': 'Synse RS-485 Bridge v1.0'
            }
        )

    def create_modbus_client(self):
        """Production hardware only wrapper for creating the serial device that
         we use to speak modbus to the CEC (Central Exhaust Chamber) board.
         This will not work for the emulator.
         :returns: The dkmodbus client."""
        # Test that the usb device is there. If not, reset the usb.
        if not os.path.exists(self.device_name):
            dkmodbus.dkmodbus.reset_usb([1, 2])

        ser = serial.Serial(self.device_name,  # Serial device name.
                            baudrate=self.baud_rate, parity=self.parity, timeout=self.timeout)
        return dkmodbus.dkmodbus(ser)

    def _set_hardware_type(self, hardware_type):
        """Known hardware types are emulator and production. Check that the
        parameter is known and set self.hardware_type.
        :param hardware_type: The hardware_type the caller would like to set.
        :raises SynseException: The given hardware_type is not known."""
        known = ['emulator', 'production']
        if hardware_type not in known:
            raise SynseException(
                RS485Device.HARDWARE_TYPE_UNKNOWN.format(hardware_type))
        self.hardware_type = hardware_type

    @staticmethod
    def _is_vec_leader_crate_stack():
        """Return true if this VEC is the leader, else False.
        :returns: True if this VEC is the leader, else False."""
        with open('/crate/mount/.state-file') as f:
            data = json.load(f)
            if data['VAPOR_VEC_LEADER'] == data['VAPOR_VEC_IP']:
                logger.debug('is_vec_leader_crate_stack: True')
                return True
            logger.debug('is_vec_leader_crate_stack: False')
        return False

    @staticmethod
    def _is_vec_leader_k8_stack():
        """Return true if this VEC is the leader, else False.
        :returns: True if this VEC is the leader, else False."""
        leader = RS485Device._get_vec_leader_k8_stack()
        if leader is not None:
            self = os.environ['POD_IP']
            logger.debug('leader is: {}'.format(leader))
            logger.debug('self is: {}'.format(self))
            return self == leader

        return False

    @staticmethod
    def is_vec_leader():
        """Return true if this VEC is the leader, else False.
        :returns: True if this VEC is the leader, else False."""
        # Try the new stack first, then fall back to the old stack.
        is_leader = RS485Device._is_vec_leader_k8_stack()
        if is_leader:
            return is_leader
        is_leader = RS485Device._is_vec_leader_crate_stack()
        return is_leader

    @staticmethod
    def _get_vec_leader_crate_stack():
        """Get the VEC leader when using the k8 stack. (old stack)
        :returns: The VEC leader IP address."""
        with open('/crate/mount/.state-file') as f:
            data = json.load(f)
            leader = data['VAPOR_VEC_LEADER']
            logger.debug('leader: {}'.format(leader))
            return leader

    @staticmethod
    def _get_vec_leader_k8_stack():
        """Get the VEC leader when using the k8 stack. (new stack)
        :returns: The VEC leader IP address."""
        try:
            r = requests.get('http://elector-headless:2288/status')
            logger.debug('request for vec leader: {}'.format(r))
            leader = None
            if r.ok:
                data = r.json()
                logger.debug('data: {}'.format(data))
                for k, v in data['members'].iteritems():
                    if v == 'leader':
                        leader = k
                        break
            else:
                logger.error('Could not determine the leader for k8 stack: {}'.format(r))
                return None
        except requests.exceptions.ConnectionError:
            logger.info('Unable to get vec leader from the k8 stack. Will try with the crate stack.')
            return None

        logger.debug('leader: {}'.format(leader))
        return leader

    @staticmethod
    def _get_vec_leader():
        """Return the VEC leader IP address.
        :returns: The VEC leader IP address."""
        # Try the new stack first, then fall back to the old stack.
        leader = RS485Device._get_vec_leader_k8_stack()
        if leader is not None:
            return leader
        return RS485Device._get_vec_leader_crate_stack()

    @staticmethod
    def redirect_call_to_vec_leader(local_url):
        """All VECs in the chamber have a connection to the same VEC USB board.
        We need to provide a sense of bus ownership (one VEC that owns the bus)
        in order to avoid bus collisions. We designate the VEC leader as the
        owner. Therefore when web requests come in on VEC that is not the
        leader, we redirect them to the leader.
        :param local_url: The web request url on the local VEC.
        :returns: The json response of the same url redirected to the VEC
        leader."""
        vec_leader_ip = RS485Device._get_vec_leader()
        parse = urlparse(local_url)
        hostname = parse.hostname
        redirect_url = string.replace(local_url, hostname, vec_leader_ip)
        logger.debug('redirect url is: {}'.format(redirect_url))
        r = http.get(redirect_url)
        return r.json()
