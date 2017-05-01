#!/usr/bin/env python
""" OpenDCRE Southbound UPS MIB upsBypass Headers Table.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class UpsBypassHeadersTable(SnmpTable):
    """SNMP table specific to the UPS MIB."""

    def __init__(self, **kwargs):

        super(UpsBypassHeadersTable, self).__init__(
            table_name='UPS-MIB-UPS-Bypass-Headers-Table',
            walk_oid='1.3.6.1.2.1.33.1.5',
            flattened_table=True,
            column_list=[
                'frequency',
                'number_of_lines',
            ],
            snmp_server=kwargs['snmp_server'],
        )
