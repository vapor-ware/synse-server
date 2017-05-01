#!/usr/bin/env python
""" OpenDCRE Southbound UPS MIB upsFullGroups Table.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class UpsFullGroupsTable(SnmpTable):
    """SNMP table specific to the UPS MIB."""

    def __init__(self, **kwargs):

        super(UpsFullGroupsTable, self).__init__(
            table_name='UPS-MIB-UPS-Full-Groups-Table',
            walk_oid='1.3.6.1.2.1.33.3.2.3',
            column_list=[
                'identity',
                'battery',
                'input',
                'output',
                'bypass',
                'alarm',
                'test',
                'control',
                'config',
            ],
            snmp_server=kwargs['snmp_server'],
        )
