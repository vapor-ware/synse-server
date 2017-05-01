#!/usr/bin/env python
""" OpenDCRE Southbound UPS MIB upsOutput Headers Table.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class UpsOutputHeadersTable(SnmpTable):
    """SNMP table specific to the UPS MIB."""

    def __init__(self, **kwargs):

        super(UpsOutputHeadersTable, self).__init__(
            table_name='UPS-MIB-UPS-Output-Headers-Table',
            walk_oid='1.3.6.1.2.1.33.1.4',
            flattened_table=True,
            column_list=[
                'source',
                'frequency',
                'number_of_lines',
            ],
            snmp_server=kwargs['snmp_server'],
        )
