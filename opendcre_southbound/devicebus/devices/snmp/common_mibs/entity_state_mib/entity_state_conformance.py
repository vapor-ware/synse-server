#!/usr/bin/env python
""" OpenDCRE Southbound Entity MIB entityState entStateConformanceTable.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class EntityStateConformanceTable(SnmpTable):
    """SNMP table specific to the Entity State MIB. We have no data from Rittal
    on these OIDs so this is untested."""

    def __init__(self, **kwargs):

        super(EntityStateConformanceTable, self).__init__(
            table_name='Entity-MIB-Entity-State-Conformance-Table',
            walk_oid='1.3.6.1.2.1.131.2.1',
            row_base='1',
            index_column='1',
            column_list=[
                'compliance',
            ],
            snmp_server=kwargs['snmp_server'],
        )
