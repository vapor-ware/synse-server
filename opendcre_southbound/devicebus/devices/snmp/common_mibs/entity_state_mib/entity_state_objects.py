#!/usr/bin/env python
""" OpenDCRE Southbound Entity MIB entityState entStateObjectsTable.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class EntityStateObjectsTable(SnmpTable):
    """SNMP table specific to the Entity State MIB."""

    def __init__(self, **kwargs):

        super(EntityStateObjectsTable, self).__init__(
            table_name='Entity-MIB-Entity-State-Objects-Table',
            walk_oid='1.3.6.1.2.1.131.1',
            row_base='1.1',
            index_column='2',
            column_list=[
                'last_changed',
                'admin',
                'operational',
                'usage',
                'alarm',
                'standby',
            ],
            snmp_server=kwargs['snmp_server'],
        )
