#!/usr/bin/env python
""" OpenDCRE Southbound UPS MIB upsSubsetGroups Table.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class UpsSubsetGroupsTable(SnmpTable):
    """SNMP table specific to the UPS MIB."""

    def __init__(self, **kwargs):

        super(UpsSubsetGroupsTable, self).__init__(
            table_name='UPS-MIB-UPS-Subset-Groups-Table',
            walk_oid='1.3.6.1.2.1.33.3.2.1',
            column_list=[
                'identity',
                'battery',
                'input',
                'output',
                'alarm',
                'control',
                'config',
            ],
            snmp_server=kwargs['snmp_server'],
        )
