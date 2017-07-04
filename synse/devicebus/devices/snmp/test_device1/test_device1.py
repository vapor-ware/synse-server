#!/usr/bin/env python
""" Synse SNMP testDevice1 Implementation.

This is a made up device to test Synse commands to an SNMP server that
another device will not support.

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
import time

from pysnmp.proto.rfc1902 import Integer, Integer32, ObjectName

from synse import constants

from .....devicebus.constants import CommandId as cid
from .....devicebus.response import Response
from .....errors import CommandNotSupported
from ..snmp_server_base import SnmpServerBase
from .tables.fan_table import FanTable
from .tables.led_table import LedTable
from .tables.power_table import PowerTable

logger = logging.getLogger(__name__)


class TestDevice1(SnmpServerBase):
    """ Device bus Interface for SNMP commands to the Synse-testDevice1 SNMP Server.
    This is a specific SNMP device/server interface for the Synse-testDevice1 Server.
    """

    # FIXME (etd) - should this be **kwargs?
    def __init__(self, app_cfg, kwargs):
        """ Construct the command map and do a scan.

        Args:
            app_cfg: the app config from Flask.
            kwargs (dict): same kwargs as passed to SnmpDevice.
        """
        logger.debug('Initializing testDevice1')
        logger.debug('testDevice1 kwargs: {}'.format(kwargs))
        super(TestDevice1, self).__init__(app_cfg, kwargs)

        # Command map specific to this type of SNMP Server.
        self._command_map[cid.READ] = self._read
        self._command_map[cid.POWER] = self._power
        self._command_map[cid.LED] = self._led
        self._command_map[cid.FAN] = self._fan

        # Run a scan on initialization to discover devices.
        # This call will setup internal tables.
        self.fan_table = None
        self.led_table = None
        self.power_table = None
        self._scan_internal()
        logger.debug('Initialized testDevice1')

    def __str__(self):
        return '<testDevice1 (server: {})>'.format(
            self.snmp_client.snmp_server)

    # region Commands
    def _fan(self, command):
        """ Synse API fan command implementation for the TestDevice1 SNMP
        server.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object for the incoming Command object
                containing the data for the fan response.
        """
        logger.debug('TestDevice1 _fan')
        logger.debug('vars(command) {}'.format(vars(command)))

        # Find the device to write.
        device = self.get_device_from_command(command)
        base_oid = device['snmp_row']['base_oid']       # base_oid of the row we need to write.
        table_name = device['snmp_row']['table_name']   # Which table to write

        if table_name != 'Synse-TestDevice1-Fan-Table':
            raise CommandNotSupported('Fan command not supported on this device.')

        # The index of the oid we need to write is the index of rpm in the
        # table + 1 because SNMP is one based and not zero based.
        write_index = self.fan_table.column_list.index('rpm') + 1
        # The OID we need to write is below.
        write_oid = base_oid.format(write_index)
        logger.debug('write_oid {}'.format(write_oid))

        # SNMP write as a tuple of (OID, data).
        # data needs to be converted to the correct SNMP type.
        fan_speed = Integer(int(command.data['fan_speed']))
        data = (ObjectName(write_oid), fan_speed)
        result = self.snmp_client.set(data)

        # Result[1] is the written fan_speed.
        written = int(result[1])
        logger.debug('written {}'.format(written))

        # Update table data. Generate and return response.
        self.fan_table.update_cell(base_oid, write_index, written)
        response_data = {'health': 'ok', 'states': [], 'speed_rpm': written}

        return Response(
            command=command,
            response_data=response_data
        )

    def _led(self, command):
        """ Synse API LED command implementation for the TestDevice1 SNMP
        server.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Response: a Response object for the incoming Command object
                containing the data for the LED response.
        """
        logger.debug('TestDevice1 _led')
        logger.debug('vars(command) {}'.format(vars(command)))

        # Find the device from the command.
        device = self.get_device_from_command(command)
        logger.debug('_led found device: {}'.format(device))

        # This is how we map the SNMP internal scan results to a device.
        # The caller to scan never sees this.
        base_oid = device['snmp_row']['base_oid']  # base_oid of the row for the device.
        table_name = device['snmp_row']['table_name']  # Which table to read.

        if table_name != 'Synse-TestDevice1-Led-Table':
            raise CommandNotSupported('LED command not supported on this device.')

        response_data = self._led_internal(command, base_oid)
        return Response(
            command=command,
            response_data=response_data
        )

    def _power(self, command):
        """ Synse API power command implementation for the TestDevice1 SNMP
        server.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Request: a Request object corresponding to the incoming Command
                object, containing the data from the power response.
        """
        logger.debug('TestDevice1 _power')
        logger.debug('vars(command) {}'.format(vars(command)))

        # Find the device to read.
        device = self.get_device_from_command(command)
        logger.debug('_power found device: {}'.format(device))

        base_oid = device['snmp_row']['base_oid']       # base_oid of the row we need to read.
        table_name = device['snmp_row']['table_name']   # Which table to read

        if table_name != 'Synse-TestDevice1-Power-Table':
            raise CommandNotSupported('Power command not supported on this device.')

        response_data = self._power_internal(command, base_oid)
        return Response(
            command=command,
            response_data=response_data
        )

    def _read(self, command):
        """ Synse API read command implementation for the TestDevice1 SNMP
        server.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Request: a Request object corresponding to the incoming Command
                object, containing the data from the read response.
        """
        logger.debug('TestDevice1 _read')
        logger.debug('vars(command) {}'.format(vars(command)))

        # Find the device to read.
        device = self.get_device_from_command(command)
        logger.debug('_read found device: {}'.format(device))

        base_oid = device['snmp_row']['base_oid']       # base_oid of the row we need to read.
        table_name = device['snmp_row']['table_name']   # Which table to read

        if table_name == 'Synse-TestDevice1-Fan-Table':
            table = self.fan_table
        elif table_name == 'Synse-TestDevice1-Power-Table':
            table = self.power_table
        else:
            raise CommandNotSupported('Unsupported command {}'.format(table_name))

        # Find the current row with the same base oid in the table.
        snmp_row = table.get(base_oid)

        # Read the same row from the SNMP server and translate it to SnmpRow.
        read_snmp_row = self.read_row(table, snmp_row)
        read_snmp_row.dump()

        # Get response data for a successful read. raise if unable to.
        response_data = table.get_row_reading(read_snmp_row, None)

        # Now that we have a valid read to return, update our table with the
        # data we read from the SNMP server.
        table.update(read_snmp_row)

        return Response(
            command=command,
            response_data=response_data
        )

    # endregion

    # region private non-command map methods.

    def _led_internal(self, command, base_oid):
        """ Lower level of the LED command.
        """
        logger.debug('_led_internal')
        logger.debug('command: {}'.format(vars(command)))
        logger.debug('base_oid: {}'.format(base_oid))

        command_led_state = command.data['led_state']
        command_led_color = command.data['led_color']
        command_led_blink = command.data['blink_state']

        # Find the current row with the same base oid in the variable table.
        snmp_row = self.led_table.get(base_oid)

        # Read the same row from the SNMP server and translate it to SnmpRow.
        row = self.read_row(self.led_table, snmp_row)
        row.dump()

        # This takes care of the get.
        led_state = TestDevice1._translate_led_state(row['state'])
        led_color = TestDevice1._translate_led_color(row['color'])
        led_blink = TestDevice1._translate_led_blink_state(row['blink_state'])

        if command_led_state is not None:
            led_state = self._set_led_state(base_oid, command_led_state)

        if command_led_color is not None and command_led_blink is not None:
            led_color = self._set_led_color(base_oid, command_led_color)
            led_blink = self._set_led_blink(base_oid, command_led_blink)
        elif command_led_color is None and command_led_blink is None:
            pass  # Nothing more to do.
        else:
            # Per the doc you need both.
            # This code will not currently run since the blueprint does not exist.
            raise CommandNotSupported('Setting color and blink state requires both to be defined.')

        response_data = {
            'led_state': led_state,
            'led_color': led_color,
            'blink_state': led_blink,
        }
        return response_data

    # NOTE: Isn't snmp_server just self here?
    # NO but comes from self: self.device_config['connection']['snmp_server']
    def _read_test_device1(self, scan_results, snmp_server, rack_id):
        """ At this point we know we are reading the device we are responsible
        for in the scan. Create the internal scan results.

        Args:
            scan_results (dict): accumulator for the internal scan results.
            snmp_server (str): the name of the SNMP server from the caller's
                device_config. example 'snmp-emulator-synse-testdevice1-board2'.
            rack_id (str): the rack id where the snmp_server is located. example 'rack_1'.
        """
        logger.debug('scanning TestDevice1')
        logger.debug('rack_id {}'.format(rack_id))

        # Get a board id if we do not already have one.
        if self.board_id is None:
            counter = self._app_cfg['SNMP_BOARD_OFFSET']
            self.board_id = counter.next() + constants.SNMP_BOARD_RANGE[0]

        # Reset the device ids we dole out here rather than in the tables since
        # we have multiple tables.
        self.reset_next_device_id()

        self._read_tables()  # Walk fan, power, and led tables.

        scan_devices = []

        # Get scan devices for each SNMP table.
        fan_devices = self.fan_table.get_scan_devices()
        scan_devices += fan_devices
        led_devices = self.led_table.get_scan_devices()
        scan_devices += led_devices
        power_devices = self.power_table.get_scan_devices()
        scan_devices += power_devices

        scan_rack = {
            'hostnames': [],
            'ip_addresses': [],
            'rack_id': rack_id,
        }
        scan_boards = []

        scan_board = {'board_id': '{0:08x}'.format(self.board_id), 'devices': scan_devices}
        scan_boards.append(scan_board)

        scan_rack['hostnames'].append(snmp_server)
        scan_rack['ip_addresses'].append(snmp_server)

        scan_rack['boards'] = scan_boards
        scan_results['racks'].append(scan_rack)

    def _read_tables(self):
        """ Create and load fan, power, and LED tables.
        """
        self.fan_table = FanTable(snmp_server=self)
        self.led_table = LedTable(snmp_server=self)
        self.power_table = PowerTable(snmp_server=self)

    def _power_internal(self, command, base_oid):
        """ Lower level of the power command.
        """
        logger.debug('_power_internal')
        logger.debug('command: {}'.format(vars(command)))
        logger.debug('base_oid: {}'.format(base_oid))

        command_action = command.data['power_action']

        # Find the current row with the same base oid in the table.
        snmp_row = self.power_table.get(base_oid)

        # Read the same row from the SNMP server and translate it to SnmpRow.
        row = self.read_row(self.power_table, snmp_row)
        row.dump()

        if command_action == 'status':
            power_state = TestDevice1._translate_power_state(row['state'])

        elif command_action == 'cycle':
            power_state = self._set_power_cycle(base_oid)

        elif command_action == 'off':
            power_state = self._set_power_off(base_oid)

        elif command_action == 'on':
            power_state = self._set_power_on(base_oid)

        else:
            raise CommandNotSupported('Device does not support setting power.')

        # Now that we have a valid read to return, update our table with the
        # data we read from the SNMP server.
        self.power_table.update(row)

        response_data = {
            'input_power': row['voltage'],
            'over_current': False,
            'power_ok': True,
            'power_status': power_state,
        }
        return response_data

    def _scan_internal(self):
        """ Internal scan results with private data including a mapping of
        devices to SNMP rows.
        """
        logger.debug('TestDevice1 _scan_internal.')

        scan_results = {'racks': []}
        logger.debug('TestDevice1 _scan_internal. Scanning TestDevice1, rack id {}.'.format(
            self.rack_id))
        self._read_test_device1(
            scan_results,
            self.device_config['connection']['snmp_server'],
            self.rack_id)

        self._scan_results_internal = scan_results

        # Trace this for now.
        logger.debug('TestDevice1 Internal scan results:')
        logger.debug(json.dumps(
            self._scan_results_internal,
            sort_keys=True,
            indent=4,
            separators=(',', ': ')))

    def _set_led_blink(self, base_oid, command_led_blink):
        """ Set LED blink state and return the SNMP data we set.

        Args:
            base_oid (str): the base SNMP OID for the LED device. The device to
                base_oid mapping will show up in the internal scan results.
            command_led_blink (str): this is 'blink' or 'steady' from the URI.

        Returns:
            str: the led blink_state as a string for the response, either
                'blink' or 'steady'.
        """
        if command_led_blink == 'steady':
            data = Integer(1)
        elif command_led_blink == 'blink':
            data = Integer(2)
        else:
            raise ValueError('LED color can only be blink or steady, got {}.'.format(
                command_led_blink))  # TODO: Test
        write_oid, write_index = self.get_write_oid(
            self.led_table, base_oid, 'blink_state')
        result = self.snmp_set(write_oid, data)

        # Result[1] is the written led state.
        written = int(result[1])
        logger.debug('written {}'.format(written))
        led_blink = TestDevice1._translate_led_blink_state(written)

        # Update table data. Return the set state.
        self.led_table.update_cell(base_oid, write_index, written)
        return led_blink

    def _set_led_color(self, base_oid, command_led_color):
        """ Set LED color and return the SNMP data we set.

        Args:
            base_oid (str): the base SNMP OID for the LED device. the device to
                base_oid mapping will show up in the internal scan results.
            command_led_color (str): this is a 6 character (3 byte) hex string from
                the URI.

        Returns:
            str: the led color as a hex string for the response, without
                a leading 0x.
        """
        led_color_setting = int(command_led_color, 16)
        if led_color_setting > 0xFFFFFF:
            raise ValueError("Maximum color is 0xffffff, got {:6x}.".format(
                led_color_setting))

        # Convert to what pysnmp wants.
        data = Integer32(led_color_setting)

        write_oid, write_index = self.get_write_oid(
            self.led_table, base_oid, 'color')
        result = self.snmp_set(write_oid, data)

        # Result[1] is the written led state.
        written = int(result[1])
        logger.debug('written {}'.format(written))

        led_color = TestDevice1._translate_led_color(written)

        # Update table data. Return the set state.
        self.led_table.update_cell(base_oid, write_index, written)
        return led_color

    def _set_led_state(self, base_oid, command_led_state):
        """ Set LED state and return the SNMP data we set.

        Args:
            base_oid (str): the base SNMP OID for the LED device. the device to
                base_oid mapping will show up in the internal scan results.
            command_led_state (str): this is 'on' or 'off' from the URI.

        Returns:
            str: the led state as a string for the response, either 'off'
                or 'on'.
        """
        if command_led_state == 'off':
            data = Integer(1)
        elif command_led_state == 'on':
            data = Integer(2)
        else:
            raise ValueError("LED state only be on or off, got {}.".format(
                command_led_state))  # TODO: Test
        write_oid, write_index = self.get_write_oid(
            self.led_table, base_oid, 'state')
        result = self.snmp_set(write_oid, data)

        # Result[1] is the written led state.
        written = int(result[1])
        logger.debug('written {}'.format(written))
        led_state = TestDevice1._translate_led_state(written)

        # Update table data. Return the set state.
        self.led_table.update_cell(base_oid, write_index, written)
        return led_state

    def _set_power(self, base_oid, data):
        """ Set power and return the SNMP data we set.

        Args:
            base_oid (str): the base SNMP OID for the power device. the device to
                base_oid mapping will show up in the internal scan results.
            data (Integer): here this is Integer(1) for off and Integer(2) for on.

        Returns:
            str: the power state as a string for the response, either 'off'
                or 'on'.
        """
        write_oid, write_index = SnmpServerBase.get_write_oid(
            self.power_table, base_oid, 'state')
        result = self.snmp_set(write_oid, data)

        # Result[1] is the written power state.
        written = int(result[1])
        logger.debug('written {}'.format(written))
        power_state = TestDevice1._translate_power_state(written)

        # Update table data. Return the set state.
        self.power_table.update_cell(base_oid, write_index, written)
        return power_state

    def _set_power_cycle(self, base_oid):
        self._set_power_off(base_oid)
        # In practice this may be different.
        # Depends on power on delay setting for PDUs.
        # Note that we don't want to timeout the web call.
        time.sleep(.1)
        return self._set_power_on(base_oid)

    def _set_power_off(self, base_oid):
        return self._set_power(base_oid, Integer(1))

    def _set_power_on(self, base_oid):
        return self._set_power(base_oid, Integer(2))

    @staticmethod
    def _translate_led_blink_state(state):
        """ Translate the LED blink state from the SNMP int to a string.

        Args:
            state (str): the blink state as an integer. for this table 1 is
                blink off (steady) and 2 is blink on (blink).

        Returns:
            str: the blink state, either 'steady' or 'blink'.

        Raises:
            ValueError: invalid blink state specified.
        """
        if state == 1:
            state = 'steady'
        elif state == 2:
            state = 'blink'
        else:
            raise ValueError('Invalid led blink state {}.'.format(state))
        return state

    @staticmethod
    def _translate_led_color(color):
        """ Translate the LED color state from the SNMP int to a string.

        Args:
            color (int): the color state as an integer.

        Returns:
            str: a six character hex color representation.

        Raises:
            ValueError: color is out of valid range.
        """
        if color > 0xFFFFFF:
            raise ValueError('Invalid led color {}.'.format(color))
        return '{0:06x}'.format(color)

    @staticmethod
    def _translate_led_state(state):
        """ Translate the LED state from the SNMP int to a string.

        Args:
            state (int): the LED state as an integer. for this table 1 is
                off and 2 is on.

        Returns:
            str: the LED state, either 'on' or 'off'.

        Raises:
            ValueError: invalid LED state is given.
        """
        if state == 1:
            state = 'off'
        elif state == 2:
            state = 'on'
        else:
            raise ValueError('Invalid led state {}.'.format(state))
        return state

    @staticmethod
    def _translate_power_state(state):
        """ Translate the power state from the SNMP int to a string.

        Args:
            state (int): the power state as an integer. for this table 1 is
                off and 2 is on.

        Returns:
            str: the power state, ether 'on' or 'off'.

        Raises:
            ValueError: invalid power state is given.
        """
        if state == 1:
            state = 'off'
        elif state == 2:
            state = 'on'
        else:
            raise ValueError('Invalid power state {}.'.format(state))
        return state

    # endregion
