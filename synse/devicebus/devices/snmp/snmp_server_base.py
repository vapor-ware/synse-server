#!/usr/bin/env python
""" Synse Base class for specific SNMP server implementations.

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
import copy
import logging

from abc import ABCMeta, abstractmethod

from ....errors import CommandNotSupported
from ....errors import SynseException
from .snmp_row import SnmpRow
from ...constants import CommandId as cid
from ....version import __api_version__, __version__
from ....devicebus.response import Response

from pysnmp.proto.rfc1902 import Counter32
from pysnmp.proto.rfc1902 import Counter64
from pysnmp.proto.rfc1902 import Gauge32
from pysnmp.proto.rfc1902 import Integer
from pysnmp.proto.rfc1902 import Integer32
from pysnmp.proto.rfc1902 import ObjectName
from pysnmp.proto.rfc1902 import TimeTicks
from pysnmp.proto.rfc1902 import Unsigned32

logger = logging.getLogger(__name__)


class SnmpServerBase(object):
    """Abstract base class for server specific SNMP implementations.
    Contains the SNMP client, the app config, the device config, and helpers
    that should be useful in derived classes."""

    __metaclass__ = ABCMeta

    def __init__(self, app_cfg, kwargs):
        """Initialize the SNMP client, app config, and board id range for the
        base class."""

        self._app_cfg = app_cfg

        # These are required.
        self.snmp_client = kwargs['snmp_client']
        self.device_config = kwargs['device_config']
        # The scan cache needs these.
        self.board_id_range = kwargs['board_id_range']
        self.board_id_range_max = kwargs['board_id_range_max']

        self.rack_id = kwargs['rack_id']

        # Derived classes should add to the command map for whatever Synse
        # commands they support.
        self._command_map = {
            cid.SCAN: self._scan,
            cid.SCAN_ALL: self._scan_all,
            cid.VERSION: self._version,
        }

        # The base class stores internal scan results here.
        self._scan_results_internal = None
        self.board_id = None
        self._next_device_id = 0
        self._next_battery_id = 0
        self._next_input_power_id = 0
        self._next_output_power_id = 0
        self._next_bypass_power_id = 0

    def __repr__(self):
        return self.__str__()

    # region Required Implementations.

    @abstractmethod
    def _scan_internal(self):
        """This method should produce scan results for an SNMP server as a
        single board. Additionally each device has a non-public snmp_row
        field that allows Synse to map an API call to a Synse device
         to the proper row in an SNMP table on the device.

        base_oid is the SNMP OID for the row. The brackets are a placeholder
        for the SNMP row column.

        table_name is the SNMP table where the row comes from. This allows
        Synse to support multiple SNMP tables on one SNMP server.

        Example:
        {
            "racks": [
            {
            "boards": [
                {
                    "board_id": "60000000",
                    "devices": [
                        {
                            "device_id": "0000",
                            "device_info": "temperature",
                            "device_type": "temperature",
                            "snmp_row": {
                                "base_oid": "1.3.6.1.4.1.61439.6.4.2.2.1.{}.11",
                                "table_name": "Emulator-Test-Variable-Table"
                            }
                        },
                        {
                            "device_id": "0001",
                            "device_info": "temperature",
                            "device_type": "temperature",
                            "snmp_row": {
                                "base_oid": "1.3.6.1.4.1.61439.6.4.2.2.1.{}.2",
                                "table_name": "Emulator-Test-Variable-Table"
                            }
                        }
                    ]
                }
            ],
            "hostnames": [
                "snmp-emulator-test"
            ],
            "ip_addresses": [
                "snmp-emulator-test"
            ],
            "rack_id": "rack_1"
            }
            ]
        }
        """
        pass

    # endregion

    # region Common Synse commands.

    def _scan(self, command):
        """Synse API scan command implementation for an SNMP server.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Request: a Request object corresponding to the incoming Command
                object, containing the data from the scan response.
        """

        client_rack_id = command.data['rack_id']
        client_rack = self.get_rack(client_rack_id)
        if not client_rack:
            # Future: This is a REST 404. Since the board id is in the URL and
            # the board id does not exist, the Synse server is not serving
            # anything at the URL specified by the client.
            # Therefore 404 Not Found.
            raise SynseException("No rack with id {}.".format(client_rack_id))

        public_scan_results = self.get_public_scan_results()

        # Filter rack and board.
        client_board_id = command.data['board_id']
        client_board_id = '{0:08x}'.format(client_board_id)  # Convert from int to string.

        # Find the rack that the client provided.
        racks = [r for r in public_scan_results['racks'] if r['rack_id'] == client_rack_id]
        # If the rack does not exist, error out.
        if not racks:
            raise SynseException('No rack with id {}.'.format(client_rack_id))
        rack = racks[0]

        if client_board_id is not None:
            # Find the board that the client provided.
            boards = [b for b in rack['boards'] if b['board_id'] == client_board_id]
            # If the board does not exist, error out.
            if not boards:
                raise SynseException('No board with id {}.'.format(client_board_id))
            else:
                rack['boards'] = boards
        return Response(command=command, response_data=public_scan_results)

    def _scan_all(self, command):
        """Synse API scan all command implementation for an SNMP server.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Request: a Request object corresponding to the incoming Command
                object, containing the data from the scan all response.
        """
        force = command.data['force']
        if force:
            try:
                self._scan_internal()  # Update scan results including private data.
            except Exception as e:
                # Device scan failures cannot take down Synse.
                # CONSIDER: Should we have a notification here?
                # (There is a ticket on this. Need to find the number.)
                logger.exception(e)
                self._scan_results_internal = None

        public_scan_results = self.get_public_scan_results()
        return Response(command=command, response_data=public_scan_results)

    def _version(self, command):
        """ Get the version information for a given board.

        Args:
            command (Command): the command issued by the Synse endpoint
                containing the data and sequence for the request.

        Returns:
            Request: a Request object corresponding to the incoming Command
                object, containing the data from the version response.
        """
        # Make sure that the board exists.
        board_id = '{0:08x}'.format(command.data['board_id'])  # Convert from int to string.
        board = self.get_board_on_rack(command.data['rack_id'], board_id)
        if not board:
            # Future: This is a REST 404. Since the board id is in the URL and
            # the board id does not exist, the Synse server is not serving
            # anything at the URL specified by the client.
            # Therefore 404 Not Found.
            raise SynseException("No board on rack {} with id {}.".format(
                command.data['rack_id'], board_id))

        return Response(
            command=command,
            response_data={
                'api_version': __api_version__,
                'synse_version': __version__,
                'snmp_version': self.snmp_client.snmp_version
            }
        )
    # endregion

    # region Protected Helpers

    @staticmethod
    def convert_snmp_result_set(results):
        """Raw walk results and aggregated get results from SNMP client are
        heavily typed, for example some rows:
        [ObjectType(ObjectIdentity(ObjectName('1.3.6.1.4.1.61439.6.5.1.2.1.8.19')), OctetString('Portez ce'))]
        [ObjectType(ObjectIdentity(ObjectName('1.3.6.1.4.1.61439.6.5.1.2.1.9.15')), Integer(25))]

        It's easier to work with a dictionary of string OIDs and data values, for example:
        '1.3.6.1.4.1.61439.6.4.2.2.1.6.23': 17
        '1.3.6.1.4.1.61439.6.4.2.2.1.3.6': 'TestPowerVariable'

        :param results: The raw walk results from SnmpClient.walk()
        :return: Converted walk results as a dictionary.
        """
        converted = {}
        for row in results:
            oid = str(row[0][0].getOid())
            if isinstance(row[0][1],
                          (Counter32, Counter64, Gauge32, TimeTicks, Integer32, Integer, Unsigned32)):
                converted_data = int(row[0][1])
            else:
                converted_data = str(row[0][1])
            converted[oid] = converted_data
        return converted

    def get_board_on_any_rack(self, board_id):
        """Get the board from the internal scan results given the board id.
        This call will check all racks.
        board_id is an 8 character hex string without the leading 0x. Example 60000000"""
        logger.debug('_get_board_on_any_rack {}'.format(board_id))
        if self._scan_results_internal is not None:
            for rack in self._scan_results_internal['racks']:
                logger.debug('rack_id: {}'.format(rack['rack_id']))
                for board in rack['boards']:
                    logger.debug('checking board with id {}'.format(board['board_id']))
                    if board['board_id'] == board_id:
                        return board
        return None  # Not found.

    def get_board_on_rack(self, rack_id, board_id):
        """Get the board from the internal scan results given the board id.
        board_id is an 8 character hex string without the leading 0x. Example 60000000"""
        logger.debug('_get_board_on_any_rack {}'.format(board_id))
        logger.debug('get_board_on_rack {} {}'.format(rack_id, board_id))
        if self._scan_results_internal is not None:
            for rack in self._scan_results_internal['racks']:
                if rack['rack_id'] != rack_id:
                    continue
                for board in rack['boards']:
                    logger.debug('checking board with id {}'.format(board['board_id']))
                    if board['board_id'] == board_id:
                        return board
        return None  # Not found.

    @staticmethod
    def get_device(board, device_id):
        """"Get the device from the internal scan results given the board and
        the device_id.
        :param board: The board id to find the device on.
        :param device_id: The id of the device to find."""
        for device in board['devices']:
            if device['device_id'] == device_id:
                return device
        return None

    def get_device_from_command(self, command):
        """Parameter validator. Returns the device. Throws if not found."""
        # Get the board (snmp-server)
        board_id = '{0:08x}'.format(command.data['board_id'])  # Convert from int to string.
        board = self.get_board_on_any_rack(board_id)
        if not board:
            # Future: This is a REST 404. Since the board id is in the URL and
            # the board id does not exist, the Synse server is not serving
            # anything at the URL specified by the client.
            # Therefore 404 Not Found.
            raise SynseException("No board with id {}.".format(board_id))

        device_id = '{0:04x}'.format(command.data['device_id'])
        device = SnmpServerBase.get_device(board, device_id)
        if not device:
            # Future: This is a REST 404. Since the board id is in the URL and
            # the device id does not exist, the Synse server is not serving
            # anything at the URL specified by the client.
            # Therefore 404 Not Found.
            raise SynseException("No device with id {}.".format(device_id))

        return device

    def get_next_battery_id(self):
        """Get the next battery id to use on a scan for this SNMP server (board).
        """
        result = self._next_battery_id
        self._next_battery_id += 1
        return '{0:0{1}x}'.format(result, 4)

    def get_next_bypass_power_id(self):
        """Get the next bypass power id to use on a scan for this SNMP server (board).
        """
        result = self._next_bypass_power_id
        self._next_bypass_power_id += 1
        return '{0:0{1}x}'.format(result, 4)

    def get_next_device_id(self):
        """Get the next device id to use on a scan for this SNMP server (board).
        """
        result = self._next_device_id
        self._next_device_id += 1
        return '{0:0{1}x}'.format(result, 4)

    def get_next_input_power_id(self):
        """Get the next input power id to use on a scan for this SNMP server (board).
        """
        result = self._next_input_power_id
        self._next_input_power_id += 1
        return '{0:0{1}x}'.format(result, 4)

    def get_next_output_power_id(self):
        """Get the next output power id to use on a scan for this SNMP server (board).
        """
        result = self._next_output_power_id
        self._next_output_power_id += 1
        return '{0:0{1}x}'.format(result, 4)

    def get_rack(self, rack_id):
        """Get the rack from the internal scan results given the rack id."""
        logger.debug('_get_rack {}'.format(rack_id))
        if self._scan_results_internal is not None:
            for rack in self._scan_results_internal['racks']:
                if rack['rack_id'] == rack_id:
                    return rack
        return None  # Not found.

    def get_public_scan_results(self):
        """Get the public part of the scan all results from the internal cache."""
        public_scan_results = copy.deepcopy(self._scan_results_internal)

        # Strip out the SNMP rows in the private data.
        if self._scan_results_internal is not None:
            if 'racks' in self._scan_results_internal:
                for rack in public_scan_results['racks']:
                    if 'boards' in rack:
                        for board in rack['boards']:
                            if 'devices' in board:
                                for device in board['devices']:
                                    del device['snmp_row']

        return public_scan_results

    @staticmethod
    def get_write_oid(table, base_oid, column_name):
        """Get the SNMP OID to write to for an SNMP set.
        :param table: Identifies the SnmpTable to write to.
        :param base_oid: Identifies the row. Same as in the internal scan cache
         for the device.
        :param column_name: Identifies the column name to write to in the table
         (string).
        :return: The OID to write and the SNMP column index to write to.
        """
        logger.debug('get_write_oid base_oid, column_name: {}, {}'.format(base_oid, column_name))
        # The index of the oid we need to write is the index of rpm in the
        # table + 1 because SNMP is one based and not zero based.
        write_index = table.column_list.index(column_name) + 1
        # The OID we need to write is below.
        logger.debug('write_index {}'.format(write_index))
        write_oid = base_oid.format(write_index)
        logger.debug('write_oid {}'.format(write_oid))
        return write_oid, write_index

    def read_row(self, table, snmp_row):
        """Wrapper for reading a row.
        Does the SNMP read from the SNMP server at each OID in the row.
        Sorts the data by column index in the table.
        Creates an SnmpRow with the newly read data and returns it.
        :param table: The table to read from.
        :param snmp_row: The row to read from the SNMP server. snmp_row comes
        from the scan results."""
        raw_row = self._read_raw_row(snmp_row)
        sorted_row_data = SnmpServerBase._sort_raw_row(table, snmp_row, raw_row)
        result = SnmpRow(
            base_oid=snmp_row.base_oid,
            table=table,
            row_data=sorted_row_data
        )
        return result

    def read_table(self, oid):
        """SNMP walk a table a the given SNMP OID and return the results in a
        usable format that can be passed to an SnmpTable constructor.
        :param oid: The base oid to SNMP walk to get the table data."""
        var_binds = self.snmp_client.walk(oid)
        result = SnmpServerBase.convert_snmp_result_set(var_binds)
        logger.debug('walk count {}, result {}'.format(len(var_binds), result))
        return result

    def reset_next_device_id(self):
        """Reset to the initial device id. Called on a new scan.
        Also resetting ids for device_info.
        """
        self._next_device_id = 0
        self._next_input_power_id = 0
        self._next_output_power_id = 0
        self._next_bypass_power_id = 0
        self._next_battery_id = 0

    def run_command(self, command):
        """ Run an incoming Synse command.

        Args:
            command (Command): The incoming command object to dispatch to the appropriate
                command handler for the Devicebus object.

        Returns:
            Response: The response data for the requested Command.

        Raises:
            CommandNotSupported: The given command does not have a corresponding handler
                defined for the Devicebus instance - this means that the given instance
                does not support any actions for that command.
        """
        command_function = self._command_map.get(command.cmd_id, None)
        if command_function is None:
            raise CommandNotSupported()

        response = command_function(command)
        return response

    def snmp_set(self, write_oid, data):
        """Write to the SNMP server.
        :param write_oid: The SNMP OID to write to.
        :param data: The data to write. data needs to be converted to the
        correct SNMP type by the caller.
        :returns: The written data in result[1]."""
        logger.debug('_snmp_set write_oid, data: {}, {}'.format(write_oid, data))
        # SNMP write as a tuple of (OID, data).
        power_state = data
        data = (ObjectName(write_oid), power_state)
        result = self.snmp_client.set(data)
        return result

    # endregion

    # region Private Helpers

    def _read_raw_row(self, snmp_row):
        """Read a row from the SNMP server. Does no table specific translation.
        The OIDs we read are the same as in the given snmp_row.
        The result will be a list of OID, data."""
        column_list_len = len(snmp_row.table.column_list)
        row_data = []
        for column in range(1, column_list_len + 1):
            oid = snmp_row.base_oid.format(column)
            # logger.debug('Reading oid {}'.format(oid))
            data = self.snmp_client.get(oid)
            row_data.append(data)
        row_data = SnmpServerBase.convert_snmp_result_set(row_data)
        logger.debug('_read_raw_row returning:')
        logger.debug('{}'.format(row_data))
        return row_data

    @staticmethod
    def _sort_raw_row(table, snmp_row, raw_row):
        """We need to sort the raw SNMP read data by OID in order to line up
        the columns with those in the table. ASCII sort is insufficient.
        :param table: The table we are operating on.
        :param snmp_row: The initial row from the scan results that we are reading.
        :param raw_row: The raw SNMP read from _read_raw_row.
        """
        logger.debug('sorting read_row')
        column_index = 1
        row_data = []

        base_oid = snmp_row.base_oid

        for _ in table.column_list:                     # For each column.
            data_oid = base_oid.format(column_index)    # Get the OID for the cell.
            row_data.append(raw_row[data_oid])          # Append the data.
            column_index += 1

        logger.debug('_sort_raw_row returning:')
        logger.debug('{}'.format(row_data))
        return row_data  # Return the data.

    # endregion
