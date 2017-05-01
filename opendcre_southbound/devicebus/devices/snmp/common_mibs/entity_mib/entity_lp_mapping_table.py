#!/usr/bin/env python
""" OpenDCRE Southbound Entity MIB entity Logical to Physical entLPMappingTable.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class EntityLPMappingTable(SnmpTable):
    """SNMP table specific to the Entity MIB."""

    def __init__(self, **kwargs):
        super(EntityLPMappingTable, self).__init__(
            table_name='Entity-MIB-Entity-LP-Mapping-Table',
            walk_oid='1.3.6.1.2.1.47.1.3.1',
            row_base='1',
            readable_column='1',
            column_list=[
                'index',
            ],
            snmp_server=kwargs['snmp_server'],
        )
