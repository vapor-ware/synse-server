#!/usr/bin/env python
""" OpenDCRE Southbound PLC Device

    Author:  Andrew, Steven, Erick
    Date:    04/13/2015
    Update:  06/11/2015 - Add power control, remap from devices to devices. (ABC)
             09/20/2016 - Move PLC Device logic into the 'device' module (ETD)

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
import lockfile
import time
import json
import sys
from uuid import getnode as get_mac_addr

from opendcre_southbound.utils import (
    board_id_to_hex_string,
    device_id_to_hex_string,
    get_device_type_code,
    get_device_type_name
)
from opendcre_southbound.definitions import *
from opendcre_southbound.version import __version__, __api_version__
from opendcre_southbound.errors import *
from opendcre_southbound import constants as const

from opendcre_southbound.devicebus.devices.plc.conversions import *
from opendcre_southbound.devicebus.command import Command
from opendcre_southbound.devicebus.response import Response
from opendcre_southbound.devicebus.devices.serial_device import SerialDevice
from opendcre_southbound.devicebus.constants import CommandId as cid
from opendcre_southbound.devicebus.devices.plc.plc_bus import *
from opendcre_southbound.vapor_common.constants import PLC_RACK_ID


logger = logging.getLogger(__name__)


class PLCDevice(SerialDevice):
    """ Devicebus interface for PLC-routed commands.
    """
    _instance_name = 'plc'

    _device_hardware = {
        'emulator': const.DEVICEBUS_EMULATOR_V1,
        'vec': const.DEVICEBUS_VEC_V1,
        'rpi_hat': const.DEVICEBUS_RPI_HAT_V1
    }

    def __init__(self, counter, **kwargs):
        super(PLCDevice, self).__init__(lock_path=kwargs['lockfile'])

        # these are required, so if they are missing from the config
        # dict passed in, we will want the exception to propagate up
        self.device_name = kwargs['device_name']
        self.hardware_type = self._device_hardware.get(kwargs['hardware_type'], DEVICEBUS_UNKNOWN_HARDWARE)

        # these are optional values, so they may not exist in the config.
        # if they do not exist, they will hold a default value
        self.bus_timeout = kwargs.get('timeout', 0.25)
        self.bus_baud = kwargs.get('bps', 115200)
        self.retry_limit = kwargs.get('retry_limit', 3)
        self.time_slice = kwargs.get('time_slice', 75)

        # hold the reference to the app's sequence number generator
        # FIXME - passing the reference around seems weird and could make things
        # uncomfortable later on. instead, one thing to investigate would be to
        # have the counter as part of the root class for devicebus interfaces, that
        # way, all implementations of devicebus interfaces should have access to it
        # and *should* be able to increment it safely, with all other interfaces
        # respecting the incrementation...
        #
        # another potential solution here would be to store the counter in the app
        # config and have the app context be passed to the devicebus interfaces on
        # init, but that isn't too different from this.
        self._count = counter

        self._lock = lockfile.LockFile(self.serial_lock)

        self._command_map = {
            cid.VERSION: self._version,
            cid.SCAN: self._scan,
            cid.SCAN_ALL: self._scan_all,
            cid.READ: self._read,
            cid.POWER: self._power,
            cid.ASSET: self._asset,
            cid.BOOT_TARGET: self._boot_target,
            cid.CHAMBER_LED: self._chamber_led,
            cid.LED: self._led,
            cid.FAN: self._fan,
            cid.HOST_INFO: self._host_info
        }

        # since PLC devices are "dumb", meaning one device talks to a range of board_ids
        # we expose the range here.  for single-board devices, an alternate 'board_id' property is exposed.
        self.board_id_range = kwargs['board_id_range']
        self.board_id_range_max = kwargs['board_id_range_max']

    def __str__(self):
        return '<PLCDevice (name: {}, hardware: {})>'.format(self.device_name, hex(self.hardware_type))

    def __repr__(self):
        return self.__str__()

    @classmethod
    def register(cls, devicebus_config, app_config, app_cache):
        """ Register PLC devices.

        Args:
            devicebus_config (dict): a dictionary containing the devicebus configurations
                for PLC. within this dict is a list or reference to the actual configs
                for the PLC devices themselves.
            app_config (dict): Flask application config, where application-wide
                configurations and constants are stored.
            app_cache (tuple): a three-tuple which contains the mutable structures
                which make up the app's device cache and lookup tables. The first
                item is a mapping of UUIDs to the devices registered here. The second
                item is a collection of "single board devices". The third item is a
                collection of "range devices". All collections are mutated by this
                method to add all devices which are successfully registered, making
                them available to the Flask app.
        """
        cls.validate_app_state(app_cache)
        device_cache, single_board_devices, range_devices = app_cache

        device_config = cls.get_device_config(devicebus_config)
        if not device_config:
            raise ValueError('Unable to get configuration for device - unable to register.')

        # now, for each device in plc devices, we create a device instance
        if 'racks' in device_config:
            for rack in device_config['racks']:
                for plc_config in rack['devices']:

                    # drop in the board_id range corresponding to PLC
                    plc_config['board_id_range_min'] = int(plc_config.get('board_id_range_min', const.PLC_BOARD_RANGE[0]))
                    plc_config['board_id_range_max'] = int(plc_config.get('board_id_range_max', const.PLC_BOARD_RANGE[1]))
                    plc_config['board_id_range'] = (plc_config['board_id_range_min'], plc_config['board_id_range_max'])

                    plc_config['rack_id'] = rack['rack_id']
                    plc_config['board_offset'] = app_config['PLC_BOARD_OFFSET'].next()
                    plc_config['hardware_type'] = rack.get('hardware_type', 'unknown')
                    plc_config['lockfile'] = rack['lockfile']

                    # check if there are override values for the device / hardware type.
                    # override values are set by passing in arguments to the main() method
                    # which initialized the app. with OpenDCRE, this is ultimately done
                    # in the startup shell scripts.
                    if app_config['SERIAL_OVERRIDE'] is not None:
                        plc_config['device_name'] = app_config['SERIAL_OVERRIDE']

                    if app_config['HARDWARE_OVERRIDE'] is not None:
                        plc_config['hardware_type'] = app_config['HARDWARE_OVERRIDE']

                    try:
                        # generate a unique ID which will be used internally to reference the
                        # device which will be created and mapped to racks/boards.
                        plc_device = PLCDevice(
                            counter=app_config['COUNTER'],
                            **plc_config
                        )
                    except Exception as e:
                        logger.error('Error initializing device: ')
                        logger.exception(e)
                        raise

                    device_cache[plc_device.device_uuid] = plc_device

                    # this is a device which owns a range of board_ids, so it should be added to _range_devices
                    range_devices.append(plc_device)

        else:
            logger.warning('Device configuration should specify "racks"!')

    def _get_bus(self):
        """ Convenience method to get a new instance of the DeviceBus.

        Returns:
            DeviceBus: a new instance of the DeviceBus object for PLC commands.
        """
        # FIXME -- in the existing code paths, a new DeviceBus instance is created for
        # every request. unclear if that is necessary or if the same instance can be
        # reused. once this implementation matches the existing functionality, can play
        # around with this to see if it can be simplified.
        return DeviceBus(
            device_name=self.device_name,
            hardware_type=self.hardware_type,
            timeout=self.bus_timeout
        )

    def _retry_command(self, bus, request, response_cls):
        """ Retry a PLC command.

        This is a convenience method used to wrap the logic for PLC
        command retries. If a command does not succeed after retry,
        an OpenDCREException is raised.

        Args:
            bus (DeviceBus): a DeviceBus instance used for serial communication.
            request (DeviceBusPacket): the initial DeviceBus command which failed
                and triggered the retry.
            response_cls (class): the class of the expected response on retry.
                this will correspond to the type of request being made.

        Returns:
            DeviceBusPacket: the devicebus packet representing the command
                response, if successful.
        """
        retry_count = 0
        valid_response = False
        response = None

        kwargs = dict(
            board_id=request.board_id if hasattr(request, 'board_id') else None,
            device_id=request.device_id if hasattr(request, 'device_id') else None,
            device_type=request.device_type if hasattr(request, 'device_type') else None,
        )
        kwargs = {k: v for k, v in kwargs.iteritems() if v is not None}

        while retry_count < self.retry_limit and not valid_response:
            try:
                # increment the sequence number for every retry attempt
                kwargs['sequence'] = next(self._count)

                logger.debug('Retrying command: {}'.format(kwargs))
                _request = RetryCommand(**kwargs)
                bus.write(_request.serialize())
                logger.debug('>>Retry: {}'.format([hex(x) for x in _request.serialize()]))

                response = response_cls(
                    serial_reader=bus,
                    expected_sequence=_request.sequence
                )
                valid_response = True

            except (BusDataException, ChecksumException) as e:
                logger.debug('Retry command: {} ({})'.format(kwargs, e.message))
                retry_count += 1
            except Exception:
                # if the bus times out, we are out of luck and must bail out
                raise OpenDCREException('No response from command retry: {}'.format(kwargs)), None, sys.exc_info()[2]

        if not valid_response:
            logger.error('Retry limit reached. ({})'.format(kwargs))
            raise OpenDCREException('Failed command retry (retry limit reached)')

        return response

    def _version(self, command):
        """ Get the version information for a given board.

        Args:
            command (Command): the command issued by the OpenDCRE endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the version response.
        """
        with self._lock:
            bus = self._get_bus()

            # get the command data out from the incoming command
            board_id = command.data['board_id']

            request = VersionCommand(
                board_id=board_id,
                sequence=command.sequence
            )
            bus.write(request.serialize())
            logger.debug('>>Version: {}'.format([hex(x) for x in request.serialize()]))

            try:
                response = VersionResponse(
                    serial_reader=bus,
                    expected_sequence=request.sequence
                )
            except BusTimeoutException:
                raise OpenDCREException('Version Command timeout'), None, sys.exc_info()[2]
            except (BusDataException, ChecksumException):
                response = self._retry_command(bus, request, VersionResponse)

            return Response(
                command=command,
                response_data={
                    'firmware_version': response.versionString,
                    'opendcre_version': __version__,
                    'api_version': __api_version__
                }
            )

    def _scan(self, command):
        """ Get the scan information for a given board.

        Args:
            command (Command): the command issued by the OpenDCRE endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the scan response.
        """
        with self._lock:
            bus = self._get_bus()

            # get the command data out from the incoming command
            board_id = command.data['board_id']

            request = DumpCommand(
                board_id=board_id,
                sequence=command.sequence
            )

            try:
                response_dict = self._vapor_scan(request, bus)

            except Exception:
                raise OpenDCREException('Scan: Error when scanning board {}'.format(board_id)), None, sys.exc_info()[2]

            return Response(command=command, response_data=response_dict)

    def _scan_all(self, command):
        """ Get the scan information from a 'broadcast' (e.g. scan all) command.

        Args:
            command (Command): the command issued by the OpenDCRE endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the scan all response.
        """
        response_dict = {'racks': []}

        with self._lock:
            bus = self._get_bus()

            mac_addr = str(get_mac_addr())
            id_bytes = [int(mac_addr[i:i + 2], 16) for i in range(len(mac_addr) - 4, len(mac_addr), 2)]
            board_id = SCAN_ALL_BOARD_ID + (id_bytes[0] << 16) + (id_bytes[1] << 8) + self.time_slice

            request = DumpCommand(
                board_id=board_id,
                sequence=command.sequence
            )

            try:
                plc_rack = self._vapor_scan(request, bus)
                plc_rack['rack_id'] = PLC_RACK_ID
                response_dict['racks'].append(plc_rack)

            except Exception:
                raise OpenDCREException('Scan All: Error when scanning all boards.'), None, sys.exc_info()[2]

            return Response(command=command, response_data=response_dict)

    def _read(self, command):
        """ Read the data off of a given board's device.

        Args:
            command (Command): the command issued by the OpenDCRE endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the read response.
        """
        with self._lock:
            bus = self._get_bus()

            # get the command data out from the incoming command
            board_id = command.data['board_id']
            device_id = command.data['device_id']
            device_type = command.data['device_type']
            device_type_string = command.data['device_type_string']

            request = DeviceReadCommand(
                board_id=board_id,
                device_id=device_id,
                device_type=device_type,
                sequence=command.sequence
            )
            bus.write(request.serialize())
            bus.flush()

            logger.debug('>>Read: {}'.format([hex(x) for x in request.serialize()]))
            response = None

            try:
                response = DeviceReadResponse(
                    serial_reader=bus,
                    expected_sequence=request.sequence
                )
                logger.debug('<<Read: {}'.format([hex(x) for x in response.serialize()]))

            except BusTimeoutException:
                raise OpenDCREException('No response from bus on sensor read.'), None, sys.exc_info()[2]
            except (BusDataException, ChecksumException):
                response = self._retry_command(bus, request, DeviceReadResponse)

        try:
            device_type_string = device_type_string.lower()

            # for now, temperature and pressure are just a string->float, all else require int conversion
            device_raw = float(''.join([chr(x) for x in response.data]))

            if device_type_string == const.DEVICE_TEMPERATURE:
                response_data = {'temperature_c': device_raw}

            elif device_type_string == const.DEVICE_PRESSURE:
                response_data = {'pressure_kpa': device_raw}

            else:
                # for all other sensors get raw value as integer
                device_raw = int(''.join([chr(x) for x in response.data]))

                # convert raw value and jsonify the device reading
                if device_type_string == const.DEVICE_THERMISTOR:
                    response_data = {'temperature_c': convert_thermistor(device_raw)}

                elif device_type_string == const.DEVICE_HUMIDITY:
                    response_data = dict(zip(('humidity', 'temperature_c'), convert_humidity(device_raw)))

                elif device_type_string == const.DEVICE_FAN_SPEED:
                    # TODO: retrieve fan mode from the auto_fan controller
                    response_data = {'speed_rpm': device_raw, 'fan_mode': 'auto'}

                elif device_type_string == const.DEVICE_VAPOR_FAN:
                    # TODO: retrieve fan mode from the auto_fan controller
                    response_data = {'speed_rpm': device_raw, 'fan_mode': 'auto'}

                elif device_type_string == const.DEVICE_LED:
                    if device_raw not in [1, 0]:
                        raise ValueError('Invalid raw value returned: {}'.format(device_raw))
                    response_data = {'led_state': 'on' if device_raw == 1 else 'off'}

                # default - for anything we don't convert, send back raw data
                # for invalid device types / device mismatches, that gets
                # caught when the request is sent over the bus
                else:
                    response_data = {'device_raw': device_raw}

            return Response(command=command, response_data=response_data)

        except (ValueError, TypeError):
            # abort if unable to convert to int (ValueError), unable to convert to chr (TypeError)
            raise OpenDCREException('Read: Error converting device reading.'), None, sys.exc_info()[2]
        except Exception:
            # if something bad happened - all we can do is abort
            raise OpenDCREException('Read: Error converting raw value.'), None, sys.exc_info()[2]

    def _power(self, command):
        """ Power control command for a given board and device.

        Args:
            command (Command): the command issued by the OpenDCRE endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the power response.
        """
        with self._lock:
            bus = self._get_bus()

            # get the command data out from the incoming command
            power_action = command.data['power_action']
            board_id = command.data['board_id']
            device_id = command.data['device_id']
            device_type = command.data['device_type']

            request = PowerControlCommand(
                board_id=board_id,
                device_id=device_id,
                device_type=device_type,
                power_action=power_action,
                sequence=command.sequence
            )
            bus.write(request.serialize())
            logger.debug('>>Power: {}'.format([hex(x) for x in request.serialize()]))

            try:
                response = PowerControlResponse(
                    serial_reader=bus,
                    expected_sequence=request.sequence
                )
                logger.debug('<<Power: {}'.format([hex(x) for x in response.serialize()]))

            except BusTimeoutException:
                raise OpenDCREException('Power command bus timeout.'), None, sys.exc_info()[2]
            except (BusDataException, ChecksumException):
                response = self._retry_command(bus, request, PowerControlResponse)

            # get raw value as string
            try:
                pmbus_raw = ''
                for x in response.data:
                    pmbus_raw += chr(x)
                # here, we should have a comma-separated string that looks like:
                # nstatus,npower,nvoltage,ncurrent - or sstatus,ncharge
                pmbus_values = pmbus_raw.split(',')
                if len(pmbus_values) == 4:
                    status_raw = int(pmbus_values[0])
                    power_raw = int(pmbus_values[1])
                    voltage_raw = int(pmbus_values[2])
                    current_raw = int(pmbus_values[3])

                    def convert_power_status(raw):
                        return 'off' if (raw >> 6 & 0x01) == 0x01 else 'on'

                    def bit_to_bool(raw):
                        return raw == 1

                    # now, convert raw reading into subfields
                    status_converted = {
                        'pmbus_raw': pmbus_raw,
                        'power_status': convert_power_status(status_raw),
                        'power_ok': not bit_to_bool((status_raw >> 11) & 0x01),
                        'over_current': bit_to_bool((status_raw >> 4) & 0x01),
                        'under_voltage': bit_to_bool((status_raw >> 3) & 0x01),
                        'input_power': convert_direct_pmbus(power_raw, 'power'),
                        'input_voltage': convert_direct_pmbus(voltage_raw, 'voltage'),
                        'output_current': convert_direct_pmbus(current_raw, 'current')
                    }
                    return Response(command=command, response_data=status_converted)

                elif len(pmbus_values) == 2:
                    # TODO: vapor_battery - this is a shim until actual PLC protocol determined
                    status_converted = {
                        'battery_status': pmbus_values[0],
                        'battery_charge_percent': int(pmbus_values[1])
                    }
                    return Response(command=command, response_data=status_converted)
                else:
                    raise OpenDCREException('Invalid power data returned: {}'.format(pmbus_raw))

            except (ValueError, TypeError, IndexError):
                # abort if unable to convert to int (ValueError), unable to convert
                # to chr (TypeError), or if expected pmbus_values don't exist (IndexError)
                raise OpenDCREException('Power: Error converting PMBUS data.'), None, sys.exc_info()[2]
            except Exception:
                raise OpenDCREException('Power: Unexpected error when converting PMBUS data.'), None, sys.exc_info()[2]

    def _asset(self, command):
        """ Asset info command for a given board and device.

        Args:
            command (Command): the command issued by the OpenDCRE endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the asset response.
        """
        with self._lock:
            bus = self._get_bus()

            # get the command data out from the incoming command
            board_id = command.data['board_id']
            device_id = command.data['device_id']
            device_type = command.data['device_type']

            request = AssetInfoCommand(
                board_id=board_id,
                device_id=device_id,
                device_type=device_type,
                sequence=command.sequence
            )
            bus.write(request.serialize())
            logger.debug('>>Asset Info: {}'.format([hex(x) for x in request.serialize()]))

            try:
                response = AssetInfoResponse(
                    serial_reader=bus,
                    expected_sequence=request.sequence
                )
                logger.debug('<<Asset Info: {}'.format([hex(x) for x in response.serialize()]))

            except BusTimeoutException as e:
                raise OpenDCREException('Asset info command bus timeout.'), None, sys.exc_info()[2]
            except (BusDataException, ChecksumException):
                response = self._retry_command(bus, request, AssetInfoResponse)

            # get raw value as string
            try:
                asset_data = ''
                for x in response.data:
                    asset_data += chr(x)

                def convert_asset_info(raw):
                    """ Convert raw asset info to JSON.  Expects a delimited string (delimiter TBD) with 13 fields.

                    Args:
                        raw: Raw data to convert.

                    Returns: JSON dictionary from string.
                    """
                    info_raw = raw.split(',')
                    if len(info_raw) == 13:
                        return {
                            'board_info': {
                                'manufacturer': info_raw[0],
                                'part_number': info_raw[1],
                                'product_name': info_raw[2],
                                'serial_number': info_raw[3]
                            },
                            'chassis_info': {
                                'chassis_type': info_raw[4],
                                'part_number': info_raw[5],
                                'serial_number': info_raw[6]
                            },
                            'product_info': {
                                'asset_tag': info_raw[7],
                                'manufacturer': info_raw[8],
                                'part_number': info_raw[9],
                                'product_name': info_raw[10],
                                'serial_number': info_raw[11],
                                'version': info_raw[12]
                            }
                        }
                    else:
                        raise ValueError('Invalid raw asset info returned {}'.format(raw))

                return Response(command=command, response_data=convert_asset_info(asset_data))

            except (ValueError, TypeError):
                # abort if unable to convert to info string (ValueError), unable to convert to chr (TypeError)
                raise OpenDCREException('Asset Info: Error converting asset info data.'), None, sys.exc_info()[2]
            except Exception:
                raise OpenDCREException('Asset Info: Unexpected exception when converting asset info'), None, sys.exc_info()[2]

    def _boot_target(self, command):
        """ Boot target command for a given board and device.

        Args:
            command (Command): the command issued by the OpenDCRE endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the boot target response.
        """
        with self._lock:
            bus = self._get_bus()

            # get the command data out from the incoming command
            board_id = command.data['board_id']
            device_id = command.data['device_id']
            device_type = command.data['device_type']
            boot_target = command.data['boot_target']

            request = BootTargetCommand(
                board_id=board_id,
                device_id=device_id,
                device_type=device_type,
                boot_target=boot_target,
                sequence=command.sequence
            )
            bus.write(request.serialize())
            logger.debug('>>Boot Target: {}'.format([hex(x) for x in request.serialize()]))

            try:
                response = BootTargetResponse(
                    serial_reader=bus,
                    expected_sequence=request.sequence
                )
                logger.debug('<<Boot Target: {}'.format([hex(x) for x in response.serialize()]))

            except BusTimeoutException:
                raise OpenDCREException('Boot target command bus timeout.'), None, sys.exc_info()[2]
            except (BusDataException, ChecksumException):
                response = self._retry_command(bus, request, BootTargetResponse)

            # get raw value as string
            try:
                target_raw = ''
                for x in response.data:
                    target_raw += chr(x)
                # here, we should have a value in { B0, B1, B2}

                def convert_boot_target(raw):
                    if raw == 'B0':
                        return 'no_override'
                    elif raw == 'B1':
                        return 'hdd'
                    elif raw == 'B2':
                        return 'pxe'
                    else:
                        raise ValueError('Invalid raw boot target returned {}'.format(raw))

                # now, convert raw reading into subfields
                target_response = {
                    'target': convert_boot_target(target_raw)
                }
                return Response(command=command, response_data=target_response)

            except (ValueError, TypeError):
                # abort if unable to convert to target string (ValueError), unable to convert to chr (TypeError)
                raise OpenDCREException('Boot Target: Error converting boot target data.'), None, sys.exc_info()[2]
            except Exception:
                raise OpenDCREException('Boot Target: Unexpected exception when converting boot target data'), None, sys.exc_info()[2]

    def _chamber_led(self, command):
        """ Chamber LED control command.

        Args:
            command (Command): the command issued by the OpenDCRE endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the chamber LED response.
        """
        with self._lock:
            bus = self._get_bus()

            # get the command data out from the incoming command
            board_id = command.data['board_id']
            device_id = command.data['device_id']
            device_type = command.data['device_type']
            rack_id = command.data['rack_id']
            led_state = command.data['led_state']
            led_color = command.data['led_color']
            blink_state = command.data['blink_state']

            request = ChamberLedControlCommand(
                board_id=board_id,
                device_id=device_id,
                device_type=device_type,
                rack_id=rack_id,
                led_state=led_state,
                led_color=led_color,
                blink_state=blink_state,
                sequence=command.sequence
            )
            bus.write(request.serialize())
            bus.flush()

            logger.debug('>>Vapor_LED: {}'.format([hex(x) for x in request.serialize()]))

            try:
                response = ChamberLedControlResponse(
                    serial_reader=bus,
                    expected_sequence=request.sequence
                )
                logger.debug('<<Vapor_LED: {}'.format([hex(x) for x in request.serialize()]))

            except BusTimeoutException:
                raise OpenDCREException('Chamber LED command bus timeout.'), None, sys.exc_info()[2]
            except (BusDataException, ChecksumException):
                response = self._retry_command(bus, request, ChamberLedControlResponse)

            # get raw value to ensure remote device took the write.
            try:
                device_raw = str(''.join([chr(x) for x in response.data]))
            except (ValueError, TypeError) as e:
                # abort if unable to convert to int (ValueError), unable to convert to chr (TypeError)
                raise OpenDCREException('Chamber LED: Error converting device response.'), None, sys.exc_info()[2]

            # TODO: temporary response format until PLC comms finalized
            if len(device_raw.split(',')) == 3:
                control_data = device_raw.split(',')
                led_response = dict()
                led_response['led_state'] = 'on' if control_data[0] == '1' else 'off'
                led_response['led_color'] = control_data[1]
                led_response['blink_state'] = 'blink' if control_data[2] == '1' else 'steady'
                return Response(command=command, response_data=led_response)
            else:
                raise OpenDCREException('Invalid Chamber LED response data.')

    def _led(self, command):
        """ LED command for a given board and device.

        Args:
            command (Command): the command issued by the OpenDCRE endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the LED response.
        """
        # first, handle requests where we just want to get the LED state
        if command.data['led_state'] is None:
            c = Command(
                cmd_id=cid.READ,
                data={
                    'board_id': command.data['board_id'],
                    'device_id': command.data['device_id'],
                    'device_type': get_device_type_code(const.DEVICE_LED),
                    'device_type_string': const.DEVICE_LED
                },
                sequence=next(self._count)
            )
            return self._read(c)

        with self._lock:
            bus = self._get_bus()

            # get the command data out from the incoming command
            board_id = command.data['board_id']
            device_id = command.data['device_id']
            device_type = command.data['device_type']
            led_state = command.data['led_state']

            # convert led_state for plc
            led_state = '1' if led_state == 'on' else '0'

            request = DeviceWriteCommand(
                board_id=board_id,
                device_id=device_id,
                device_type=device_type,
                raw_data=led_state,
                sequence=command.sequence
            )
            bus.write(request.serialize())
            bus.flush()

            logger.debug('>>LED: {}'.format([hex(x) for x in request.serialize()]))
            response = None

            try:
                response = DeviceWriteResponse(
                    serial_reader=bus,
                    expected_sequence=request.sequence
                )
                logger.debug('<<LED: {}'.format([hex(x) for x in response.serialize()]))

            except BusTimeoutException:
                raise OpenDCREException('LED write command bus timeout.'), None, sys.exc_info()[2]
            except (BusDataException, ChecksumException):
                response = self._retry_command(bus, request, DeviceWriteResponse)

        # get raw value to ensure remote device took the write.
        try:
            device_raw = str(''.join([chr(x) for x in response.data]))
        except (ValueError, TypeError):
            # abort if unable to convert to int (ValueError), unable to convert to chr (TypeError)
            raise OpenDCREException('LED: Error converting device response.'), None, sys.exc_info()[2]
        if device_raw == 'W1':
            c = Command(
                cmd_id=cid.READ,
                data={
                    'board_id': board_id,
                    'device_id': device_id,
                    'device_type': get_device_type_code(const.DEVICE_LED),
                    'device_type_string': const.DEVICE_LED
                },
                sequence=next(self._count)
            )
            return self._read(c)
        else:
            raise OpenDCREException('Error writing to device {} on board {}'.format(hex(device_id), hex(board_id)))

    def _fan(self, command):
        """ Fan speed control command for a given board and device.

        Args:
            command (Command): the command issued by the OpenDCRE endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the fan response.
        """
        with self._lock:
            bus = self._get_bus()

            # get the command data out from the incoming command
            board_id = command.data['board_id']
            device_id = command.data['device_id']
            device_type = command.data['device_type']
            fan_speed = command.data['fan_speed']

            request = DeviceWriteCommand(
                board_id=board_id,
                device_id=device_id,
                device_type=device_type,
                raw_data=fan_speed,
                sequence=command.sequence
            )
            bus.write(request.serialize())
            bus.flush()

            logger.debug('>>Fan_Speed: {}'.format([hex(x) for x in request.serialize()]))
            response = None

            try:
                response = DeviceWriteResponse(
                    serial_reader=bus,
                    expected_sequence=request.sequence
                )
                logger.debug('<<Fan_Speed: {}'.format([hex(x) for x in response.serialize()]))

            except BusTimeoutException:
                raise OpenDCREException('Fan command bus timeout.'), None, sys.exc_info()[2]
            except (BusDataException, ChecksumException):
                response = self._retry_command(bus, request, DeviceWriteResponse)

        # get raw value to ensure remote device took the write.
        try:
            device_raw = str(''.join([chr(x) for x in response.data]))
        except (ValueError, TypeError):
            # abort if unable to convert to int (ValueError), unable to convert to chr (TypeError)
            raise OpenDCREException('Fan control: Error converting device response.'), None, sys.exc_info()[2]
        if device_raw == 'W1':
            c = Command(
                cmd_id=cid.READ,
                data={
                    'board_id': board_id,
                    'device_id': device_id,
                    'device_type': get_device_type_code(const.DEVICE_FAN_SPEED),
                    'device_type_string': const.DEVICE_FAN_SPEED
                },
                sequence=next(self._count)
            )
            return self._read(c)
        else:
            raise OpenDCREException('Error writing to device {} on board {}'.format(hex(device_id), hex(board_id)))

    def _host_info(self, command):
        """ Get the host information for a given board and device.

        Args:
            command (Command): the command issued by the OpenDCRE endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object corresponding to the incoming Command
                object, containing the data from the host info response.
        """
        with self._lock:
            bus = self._get_bus()

            # get the command data out from the incoming command
            board_id = command.data['board_id']
            device_id = command.data['device_id']
            device_type = command.data['device_type']

            request = HostInfoCommand(
                board_id=board_id,
                device_id=device_id,
                device_type=device_type,
                sequence=command.sequence
            )
            bus.write(request.serialize())
            bus.flush()

            logger.debug('>>Host_Info: {}'.format([hex(x) for x in request.serialize()]))
            response = None

            try:
                response = HostInfoResponse(
                    serial_reader=bus,
                    expected_sequence=request.sequence
                )
                logger.debug('<<Host_Info: {}'.format([hex(x) for x in response.serialize()]))

            except BusTimeoutException:
                raise OpenDCREException('Host Info command bus timeout.'), None, sys.exc_info()[2]
            except (BusDataException, ChecksumException):
                response = self._retry_command(bus, request, HostInfoResponse)

        # get raw value to ensure remote device took the write.
        try:
            device_raw = str(''.join([chr(x) for x in response.data]))
        except (ValueError, TypeError):
            # abort if unable to convert to int (ValueError), unable to convert to chr (TypeError)
            raise OpenDCREException('Host Info: Error converting device response.'), None, sys.exc_info()[2]
        # convert to json dictionary
        try:
            host_information = dict()
            host_information['ip_addresses'] = []
            host_information['hostnames'] = []
            host_fields = device_raw.split(',')
            for field in host_fields:
                if field[0] == 'i':
                    host_information['ip_addresses'].append(field[1:])
                elif field[0] == 'h':
                    host_information['hostnames'].append(field[1:])
                else:
                    raise ValueError('Invalid field in host information: {}.'.format(field))
            return Response(command=command, response_data=host_information)

        except ValueError as e:
            raise OpenDCREException(e.message)
        except Exception:
            raise OpenDCREException('Invalid host information returned'), None, sys.exc_info()[2]

    def _vapor_scan(self, packet, bus=None, retry_count=0):
        """ Query all boards and provide the active devices on each board.

        This method performs a scan operation by sending a DumpResponsePacket to
        the bus. Collisions on the bus may occur, or corrupt data may be read off
        the bus when collecting the responses. In these cases, this method employs
        a retry mechanism which first clears the bus, then re-sends the request.
        If failures continue past the configurable RETRY_LIMIT, an exception will
        be raised, indicating a problem with bus communications.

        Args:
            packet (DeviceBusPacket): the packet to send over the bus.
            bus (DeviceBus): the bus connection to send the packet over.
            retry_count (int): the number of scan retries.

        Returns:
            dict: A dictionary containing a list of all found boards, and all devices
                found on each board.

        Raises:
            BusCommunicationError: if the number of scan retries exceed the set
                RETRY_LIMIT.
        """
        response_dict = {'boards': []}
        bus.write(packet.serialize())

        logger.debug('>>Scan: {}'.format([hex(x) for x in packet.serialize()]))

        try:
            response_packet = DumpResponse(
                serial_reader=bus,
                expected_sequence=packet.sequence
            )
        except BusTimeoutException:
            raise OpenDCREException('Scan command bus timeout.'), None, sys.exc_info()[2]
        except (BusDataException, ChecksumException):
            if packet.board_id >> SCAN_ALL_BIT == 1:
                # add the shuffle bit to the packet board_id
                packet.board_id = packet.board_id | SHUFFLE_BOARD_ID
            retry_count += 1

            # flush the bus of any corrupt data
            # TODO: determine if it is necessary to wait for the timeslice to complete to flush everything out since
            # boards may still be writing
            time.sleep(0.150)
            bus.flush_all()

            # retry if permissible
            if retry_count < self.retry_limit:
                logger.debug('Sending retry packet from initial.')
                return self._vapor_scan(packet, bus, retry_count=retry_count)
            else:
                # FIXME - this exception message seems out of place.. should it only be alerting of the
                # retry limit having been reached?
                raise BusCommunicationError(
                    'Corrupt packets received (failed checksum validation) - Retry limit reached.'
                )
        else:
            response_dict['boards'].append({
                'board_id': board_id_to_hex_string(response_packet.board_id),
                'devices': [{
                    'device_id': device_id_to_hex_string(response_packet.device_id),
                    'device_type': get_device_type_name(response_packet.data[0])
                }]
            })
            logger.debug('<<Scan: {}'.format([hex(x) for x in response_packet.serialize()]))

        while True:
            try:
                response_packet = DumpResponse(
                    serial_reader=bus,
                    expected_sequence=packet.sequence
                )
            except BusTimeoutException:
                # if we get no response back from the bus, the assumption at this point is
                # that all boards/devices have been returned and there is nothing left to
                # get, so we break out of the loop and return the found results.
                break
            except (BusDataException, ChecksumException):
                if packet.board_id >> SCAN_ALL_BIT == 1:
                    # add the shuffle bit to the packet board_id
                    packet.board_id = packet.board_id | SHUFFLE_BOARD_ID
                retry_count += 1

                # flush the bus of any corrupt data
                # TODO: determine if it is necessary to wait for the timeslice to complete to flush everything out since
                # boards may still be writing
                time.sleep(0.150)
                bus.flush_all()

                # retry if permissible
                if retry_count < self.retry_limit:
                    logger.debug('Sending retry packet from retry.')
                    return self._vapor_scan(packet, bus, retry_count=retry_count)
                else:
                    raise BusCommunicationError(
                        'Corrupt packets received (failed checksum validation) - Retry limit reached.'
                    )

            else:
                board_exists = False

                # iterate through the boards to locate the board record
                # corresponding with the board_id from the response
                # if it does not exist, set a flag, so we can add the board
                # and in both cases we add a device record for the relevant board/device
                for board in response_dict['boards']:
                    if int(board['board_id'], 16) == response_packet.board_id:
                        board_exists = True
                        board['devices'].append({
                            'device_id': device_id_to_hex_string(response_packet.device_id),
                            'device_type': get_device_type_name(response_packet.data[0])
                        })
                        break

                if not board_exists:
                    response_dict['boards'].append({
                        'board_id': board_id_to_hex_string(response_packet.board_id),
                        'devices': [{
                            'device_id': device_id_to_hex_string(response_packet.device_id),
                            'device_type': get_device_type_name(response_packet.data[0])
                        }]
                    })
                logger.debug('<<Scan: {}'.format([hex(x) for x in response_packet.serialize()]))

        # if we get here, and the scan was a scan-all and successful, we can save the scan state.
        # we don't expect a response for a save command, so after writing to the
        # bus, we can return the aggregated scan results.
        if (packet.board_id >> SCAN_ALL_BIT) & 0x01 == 0x01:
            board_id = SCAN_ALL_BOARD_ID | SAVE_BOARD_ID
            save_packet = DumpCommand(
                board_id=board_id,
                sequence=next(self._count)
            )
            bus.write(save_packet.serialize())
            bus.flush_all()
            # TODO: verify that a brief delay is not needed here for hardware to commit

        return response_dict
