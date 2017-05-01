#!/usr/bin/env python
""" OpenDCRE Southbound Entity MIB entity Alias Mapping Table entAliasMappingTable.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class EntityAliasMappingTable(SnmpTable):
    """SNMP table specific to the Entity MIB."""

    def __init__(self, **kwargs):

        super(EntityAliasMappingTable, self).__init__(
            table_name='Entity-MIB-Entity-Alias-Mapping-Table',
            walk_oid='1.3.6.1.2.1.47.1.3.2',
            row_base='1',
            readable_column='2',     # This is an odd one with a row pointer.
            column_list=[
                'index_or_zero',
                'mapping_identifier',
            ],
            snmp_server=kwargs['snmp_server'],
        )
