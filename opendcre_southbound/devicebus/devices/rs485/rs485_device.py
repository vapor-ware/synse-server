#!/usr/bin/env python
""" OpenDCRE Southbound RS485 Device

    Author: Erick Daniszewski
    Date:   09/15/2016

    \\//
     \/apor IO
"""
import logging
import lockfile

from opendcre_southbound.devicebus.devices.serial_device import SerialDevice
from opendcre_southbound import constants as const
from opendcre_southbound.devicebus.constants import CommandId as cid
from opendcre_southbound.devicebus.response import Response
from opendcre_southbound.version import __api_version__, __version__

logger = logging.getLogger(__name__)


class RS485Device(SerialDevice):
    """ Base class for all RS485 device implementations.
    """
    def __init__(self, **kwargs):
        super(RS485Device, self).__init__(lock_path=kwargs['lockfile'])

        self.hardware_type = kwargs.get('hardware_type', 'unknown')

        self.device_name = kwargs['device_name']
        self.rack_id = kwargs['rack_id']
        self.unit = kwargs['device_unit']

        self.timeout = kwargs.get('timeout', 0.25)
        self.method = kwargs.get('method', 'rtu')

        self._lock = lockfile.LockFile(self.serial_lock)

        # Common RS-485 commands.
        self._command_map = {
            cid.SCAN: self._scan,
            cid.SCAN_ALL: self._scan_all,
            cid.VERSION: self._version,
        }

    def __str__(self):
        return '<{} (rack: {}, board: {:08x})>'.format(self.__class__.__name__, self.rack_id, self.board_id)

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
                    rs485_device['board_id_range'] = device_config.get('board_id_range', const.RS485_BOARD_RANGE)
                    rs485_device['hardware_type'] = rack.get('hardware_type', 'unknown')
                    rs485_device['device_name'] = rack['device_name']
                    rs485_device['lockfile'] = rack['lockfile']

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
            command (Command): the command issued by the OpenDCRE endpoint
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
            command (Command): the command issued by the OpenDCRE endpoint
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
            command (Command): the command issued by the OpenDCRE endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the version response.
        """
        return Response(
            command=command,
            response_data={
                'api_version': __api_version__,
                'opendcre_version': __version__,
                'firmware_version': 'OpenDCRE RS-485 Bridge v1.0'
            }
        )
