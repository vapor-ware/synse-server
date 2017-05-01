#!/usr/bin/env python
""" OpenDCRE Southbound UPS MIB upsInput Headers Table.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class UpsInputHeadersTable(SnmpTable):
    """SNMP table specific to the UPS MIB."""

    def __init__(self, **kwargs):

        super(UpsInputHeadersTable, self).__init__(
            table_name='UPS-MIB-UPS-Input-Headers-Table',
            walk_oid='1.3.6.1.2.1.33.1.3',
            flattened_table=True,
            column_list=[
                'line_bads',
                'number_of_lines',
            ],
            snmp_server=kwargs['snmp_server'],
        )
