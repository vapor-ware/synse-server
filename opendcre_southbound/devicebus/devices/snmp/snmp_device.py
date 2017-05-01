#!/usr/bin/env python
""" OpenDCRE Southbound SNMP Device.

    \\//
     \/apor IO
"""
import logging

from opendcre_southbound import constants as const

from .snmp_client import SnmpClient
from .snmp_server_factory import SnmpServerFactory
from ..lan_device import LANDevice
from ....devicebus.constants import CommandId as cid
from ....devicebus.response import Response

logger = logging.getLogger(__name__)


class SnmpDevice(LANDevice):
    """ Device bus Interface for SNMP routed commands.

    Each SNMP server is one SnmpDevice.

    At this level SnmpDevice is just a generic SNMP server of some sort.
    Implementation specific SNMP servers derive from SnmpServerBase.
    """

    # See docs in the base DevicebusInterface. This is used as a convenience to:
    # - Provide a more or less human readable string that describes the device.
    # - Give us a unique key to reference that instance during registration for certain device types.
    _instance_name = 'snmp'

    def __init__(self, app_cfg, **kwargs):
        super(SnmpDevice, self).__init__()

        self._app_cfg = app_cfg

        # These are required.
        self.snmp_client = kwargs['snmp_client']
        self.device_config = kwargs['device_config']

        # The scan cache needs these.
        self.board_id_range = kwargs['board_id_range']
        self.board_id_range_max = kwargs['board_id_range_max']

        self.server_type = kwargs['server_type']

        # Override the command map to defines which commands are supported
        # by SNMP.
        self._command_map = {
            cid.VERSION: self._version,
            cid.SCAN: self._scan,
            cid.SCAN_ALL: self._scan_all,
            cid.READ: self._read,
            cid.POWER: self._power,
            cid.LED: self._led,
            cid.FAN: self._fan,
        }

        self.snmp_server = SnmpServerFactory.initialize_snmp_server(
            self.server_type, app_cfg=app_cfg, kwargs=kwargs)

    def __str__(self):
        return '<SnmpDevice (server: {}, board: {})>'.format(
            self.snmp_client.snmp_server, self.snmp_server.board_id)

    def __repr__(self):
        return self.__str__()

    # region Commands

    def _fan(self, command):
        return self.run_command(command)

    def _led(self, command):
        return self.run_command(command)

    def _power(self, command):
        return self.run_command(command)

    def _read(self, command):
        return self.run_command(command)

    def _scan(self, command):
        return self.run_command(command)

    def _scan_all(self, command):
        return self.run_command(command)

    def _version(self, command):
        return self.run_command(command)

    # endregion

    # region private

    def run_command(self, command):
        """Wrapper for SnmpServerBase.run_command. This is needed when
        initialization fails for the SNMP server. OpenDCRE should continue to
        run normally and web API calls cannot access the SNMP server that
        failed to initialize."""
        if not self.snmp_server:    # Null check snmp_server.
            # If we fail to initialize a server, don't fail all of OpenDCRE.
            message = 'SNMP Server not initialized. Unable to run command.'
            logger.error(message)
            # Cannot raise here. If we raise, then one uninitialized server will break the rest on scan.
            # Return an empty response.
            # TODO: This should be a common 'do nothing' scan response including the error logging.
            # Notification should only go out on the initial scan (we told you, we didn't spam you)
            return Response(
                command=command,
                response_data={}
            )
        return self.snmp_server.run_command(command)

    # endregion

    # region public

    @classmethod
    def register(cls, devicebus_config, app_config, app_cache):
        """Register SNMP devices.

        Args:
            devicebus_config (dict): a dictionary containing the devicebus configurations
                for SNMP. within this dict is a list or reference to the actual configs
                for the SNMP devices themselves.
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

        # Load the SNMP configuration.
        device_config = cls.get_device_config(devicebus_config)
        if device_config is None:
            return False  # Registration failure. Message is in the log. Notification created.

        # Need to do an inline walk here since we don't have self yet and we
        # need to discover SNMP devices attached to the server.
        if 'racks' in device_config:
            for rack in device_config['racks']:
                for snmp_device in rack['snmp_devices']:

                    try:
                        # Create a snmp client with the connection info for the server.
                        connection = snmp_device['connection']
                        snmp_client = SnmpClient(** connection)

                        server_type = snmp_device['server_type']
                        logger.debug('SNMP server_type: {}'.format(server_type))

                        # Create and register the SNMP device.
                        snmp_device_config = {
                            'snmp_client': snmp_client,
                            'device_config': snmp_device,
                            'server_type': server_type,
                            'rack_id': rack['rack_id'],
                        }

                        # The scan cache needs these.
                        snmp_device_config['board_id_range_min'] = int(
                            snmp_device_config.get('board_id_range_min', const.SNMP_BOARD_RANGE[0]))
                        snmp_device_config['board_id_range_max'] = int(
                            snmp_device_config.get('board_id_range_max', const.SNMP_BOARD_RANGE[1]))
                        snmp_device_config['board_id_range'] = (
                            snmp_device_config['board_id_range_min'], snmp_device_config['board_id_range_max'])

                        logger.debug(
                            'Initializing SNMP Device for rack {}, snmp_device {}, snmp_device_config {}.'.format(
                                rack['rack_id'], snmp_device, snmp_device_config
                            ))
                        snmp_device = SnmpDevice(app_config, ** snmp_device_config)

                        # when an SNMP device has been successfully initialized, it will maintain its
                        # own SNMP server implementation. the SNMP server should scan on init and be
                        # assigned a board_id, if it does not already have one. since each SNMP device
                        # has only a single SNMP server implementation, we can use that same board id
                        # to identify the device bus implementation.
                        board_id = snmp_device.snmp_server.board_id
                        if not board_id:
                            logger.error(
                                'Error initializing SNMP Device {} - no board id assigned; unable to '
                                'add device to internal lookup table.'.format(snmp_device)
                            )
                        else:
                            device_cache[snmp_device.device_uuid] = snmp_device
                            single_board_devices[board_id] = snmp_device

                    except Exception as e:
                        # Log the failure, notify, and move on.
                        logger.error('Failed to initialize SNMP Device: {}'.format(snmp_device))
                        logger.exception(e)

    # endregion
