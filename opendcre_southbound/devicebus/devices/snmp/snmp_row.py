#!/usr/bin/env python
""" OpenDCRE Southbound SNMP Table.

    \\//
     \/apor IO
"""

import logging

from vapor_common.utils.argument_checker import ArgumentChecker

logger = logging.getLogger(__name__)


class SnmpRow(object):
    """Encapsulate one row of SNMP data for a table. This could also be used
    for single row SNMP queries. (TBD)"""

    def __init__(self, **kwargs):
        """Constructor."""

        # This is different than the parent table.
        # For a table row this is an oid to walk to retrieve all columns.
        # For a single row this is the oid to get to retrieve the single column.
        # Example: 1.3.6.1.4.1.61439.6.4.2.2.1.{}.<table_row_index>
        #          1.3.6.1.4.1.61439.6.4.2.2.1.{}.4
        # The one based column index will go into the {}
        self.base_oid = ArgumentChecker.check_instance(basestring, kwargs['base_oid'])

        # This will be absent for single column queries. (TBD)
        # Example: 4
        # self.table_row_index = kwargs['table_row_index']
        # Currently cannot check that this class derives from SnmpTable due to
        # circular reference.
        self.table = kwargs['table']

        # Friendly names for each column in the table.
        # Example: ['id', 'index', 'name']
        # This will come straight off of the table (no copy, just a pointer).
        # This is checked in the SnmpTable class.
        column_list = self.table.column_list

        # SNMP data for the walked row. This is a list of data for each column
        # sorted by column ordinal. It's up the caller to pre-sort.
        # First check that it is a list.
        self.row_data = ArgumentChecker.check_type('list', kwargs['row_data'])
        column_list_len = len(column_list)
        row_data_len = len(self.row_data)
        if column_list_len != row_data_len:
            raise ValueError('Given {} column names and {} data columns. '
                             'Unable to map unless equal.'.format(
                              column_list_len, row_data_len))

    def __getitem__(self, item):
        """Accesses row data as if it's a dictionary by self['column_name'].
        Internally row_data is a list to avoid additional and unnecessary copies."""
        return self.row_data[self.table.column_list.index(item)]

    def to_scan_json(self):
        """Serialize part of an SNMP row to json. This is used for/in the
        internal scan results."""
        return {'table_name': self.table.table_name, 'base_oid': self.base_oid}

    def dump(self):
        logger.debug('Dumping row for SNMP table {}'.format(self.table.table_name))
        logger.debug('base_oid: {}'.format(self.base_oid))
        index = 0
        for column_name in self.table.column_list:
            logger.debug('row[{}] = {}'.format(column_name, self.row_data[index]))
            index += 1
