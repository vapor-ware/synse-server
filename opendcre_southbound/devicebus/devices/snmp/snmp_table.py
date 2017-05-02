#!/usr/bin/env python
""" OpenDCRE Southbound SNMP Table.

    \\//
     \/apor IO
"""

import logging
import string

from binascii import hexlify
from .snmp_row import SnmpRow
from .snmp_server_base import SnmpServerBase
from vapor_common.utils.argument_checker import ArgumentChecker

logger = logging.getLogger(__name__)


class SnmpTable(object):
    """Given a base OID to walk the table with, a column list, and raw SNMP
    walk data, construct an object to translate and encapsulate into meaningful
    data."""

    def __init__(self, **kwargs):
        """Constructor."""

        # This is how we identify what table we are working on internally.
        # SnmpTable is a generic table class. VariableTable is a specific
        # table class to the Emulator Test MIB.
        self.table_name = ArgumentChecker.check_instance(basestring, kwargs['table_name'])

        # This is the OID to walk the whole table.
        self.walk_oid = ArgumentChecker.check_instance(basestring, kwargs['walk_oid'])

        # If present each row is keyed at:
        # walk_oid + '.' + row_base + '.' + <column_index> + '.' + <row_index>
        if 'row_base' in kwargs:
            self.row_base = ArgumentChecker.check_instance(basestring, kwargs['row_base'])
        else:
            self.row_base = None

        # This is appended to the walk_oid to get row indexes. The column may
        # not be readable however, in which case None is fine.
        if 'index_column' in kwargs:
            self.index_column = ArgumentChecker.check_type(
                'int', kwargs['index_column'])
        else:
            self.index_column = None

        # Required when the index_column is marked not-accessible in the MIB.
        # Provides a way to tell how many rows are in the table.
        if 'readable_column' in kwargs:
            self.readable_column = ArgumentChecker.check_type(
                'int', kwargs['readable_column'])
        else:
            self.readable_column = None

        # A flattened table is really just a group of OIDs at the same level
        # and not truly an SNMP table. It's just simpler to read it in as a
        # single row table.
        if 'flattened_table' in kwargs:
            self.flattened_table = ArgumentChecker.check_type(
                'bool', kwargs['flattened_table'])
        else:
            self.flattened_table = False

        # Friendly names for each column in the table.
        # Example: ['id', 'index', 'name']
        self.column_list = ArgumentChecker.check_type('list', kwargs['column_list'])

        # The SNMP Server (board) that this table is on. Needed for generating device ids.
        self.snmp_server = kwargs['snmp_server']

        # Load the table data on construction.
        self.rows = None
        self.load()

    def _get_row_indexes(self, table_data):

        prefix = self.walk_oid + '.'
        if self.row_base is not None:
            prefix += self.row_base + '.'

        if self.index_column is not None:
            # We can read the index column to get the row indexes.
            if self.index_column is not None:
                prefix += self.index_column + '.'

            # Get all values where the key starts with the prefix.
            row_indexes = [value for key, value in table_data.iteritems() if key.startswith(prefix)]

        else:
            # We can't read the index column. Read the column passed in at
            # self.readable_column.
            if self.readable_column is not None:
                prefix += self.readable_column + '.'

            oids = [key for key, value in table_data.iteritems() if key.startswith(prefix)]

            row_indexes = []
            for oid in oids:
                row_index = oid[len(prefix):]
                row_indexes.append(row_index)

        return row_indexes

    def _translate(self, table_data):
        """Translate into a structure of SnmpRow."""
        self.rows = []
        row_indexes = self._get_row_indexes(table_data)  # Find the row indexes.

        if not self.flattened_table:
            for row_index in row_indexes:                    # For each row.
                column_index = 1
                row_data = []

                base_oid = self.walk_oid + '.' + self.row_base + '.{}.' + str(row_index)
                for _ in self.column_list:    # For each column.
                    data_oid = base_oid.format(column_index)
                    row_data.append(table_data.get(data_oid))   # None for not-accessible columns.
                    column_index += 1

                row = SnmpRow(
                    base_oid=base_oid,
                    table=self,
                    row_data=row_data
                )
                self.rows.append(row)

        else:
            logger.debug('flattened_table')
            base_oid = self.walk_oid + '.{}.0'
            column_index = 1
            row_data = []

            for _ in self.column_list:
                data_oid = base_oid.format(column_index)
                row_data.append(table_data.get(data_oid))  # None for not-accessible columns.
                column_index += 1

            row = SnmpRow(
                base_oid=base_oid,
                table=self,
                row_data=row_data
            )
            self.rows.append(row)

    def dump(self):
        """Simple table dump to the log as CSV."""
        logger.debug('Dumping {} table. {} rows'.format(
            self.table_name, len(self.rows)))
        logger.debug(', {}'.format(','.join(self.column_list)))
        for row in self.rows:
            data = []
            for cell in row.row_data:
                if cell is None:
                    data.append('')
                elif not isinstance(cell, basestring):
                    data.append(cell)
                elif all(ord(c) < 127 and c in string.printable for c in cell):
                    data.append(cell)
                else:
                    data.append('0x' + hexlify(cell))  # Non-printable hex string.
            logger.debug(', {}'.format(','.join('{}'.format(x) for x in data)))

    def get(self, base_oid):
        """Get the row with the given base OID from the table or None if not present.
        This is just a get from the cache. It is not a get from the SNMP server."""
        for row in self.rows:
            logger.debug('base_oid {}'.format(row.base_oid))
            if row.base_oid == base_oid:
                logger.debug('found row {}'.format(row))
                return row
        return None

    def load(self):
        """Walk the walk_oid on the SNMP server. Translate the data to SnmpRows."""
        var_binds = self.snmp_server.snmp_client.walk(self.walk_oid)
        table_data = SnmpServerBase.convert_snmp_result_set(var_binds)
        self._translate(table_data)
        logger.debug('Loaded SnmpTable {}. {} row(s).'.format(
            self.table_name, len(self.rows)))

    def unload(self):
        """Unload cached row data once we're done with it. Long term we should
        only need it during a forced scan."""
        self.rows = None
        logger.debug('Unloaded SnmpTable {}.'.format(self.table_name))

    def update(self, row):
        """Update the table by removing the row with the same base_oid as row,
        then adding row from the parameter list.
        :param row: The row to update."""

        # Delete the existing SNMP row in the variable table by base_oid.
        logger.debug('before delete row count {}'.format(len(self.rows)))
        self.rows = [x for x in self.rows if x.base_oid != row.base_oid]
        logger.debug('after delete row count {}'.format(len(self.rows)))

        # Add the new row.
        self.rows.append(row)
        logger.debug('after adding the row we read row count {}'.format(len(self.rows)))

    def update_cell(self, base_oid, index, data):
        """Update the table data. Used on successful write.
        :param base_oid: The base oid of the row to update.
        :param index: The 1 based column index to update.
        :param data: The data for the update.
        """
        found_row = None
        for row in self.rows:
            if row.base_oid == base_oid:
                found_row = row
                break
        if not found_row:
            raise ValueError('Unable to find row with base oid {}'.format(base_oid))
        found_row.row_data[index - 1] = data
