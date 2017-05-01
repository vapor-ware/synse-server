#!/usr/bin/env python
""" OpenDCRE Southbound Entity MIB entityLogical entLogicalTable.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class EntityLogicalTable(SnmpTable):
    """SNMP table specific to the Entity MIB."""

    def __init__(self, **kwargs):

        super(EntityLogicalTable, self).__init__(
            table_name='Entity-MIB-Entity-Logical-Table',
            walk_oid='1.3.6.1.2.1.47.1.2',
            row_base='1.1',
            readable_column='2',
            column_list=[
                'index',
                'description',
                'type',
                'community',
                'transport_address',
                'transport_domain',
                'context_engine_id',
                'context_name',
            ],
            snmp_server=kwargs['snmp_server'],
        )
