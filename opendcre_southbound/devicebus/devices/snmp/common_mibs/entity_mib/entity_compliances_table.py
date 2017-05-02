#!/usr/bin/env python
""" OpenDCRE Southbound Entity MIB entity Logical to Physical entLPMappingTable.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class EntityCompliancesTable(SnmpTable):
    """SNMP table specific to the Entity MIB. This is just OIDs under
    1.3.6.1.2.1.47.3.1, but it's simplest to treat everything as a table.
    We do not have real data for these OIDs, so this is currently untested."""

    def __init__(self, **kwargs):

        super(EntityCompliancesTable, self).__init__(
            table_name='Entity-MIB-Entity-Compliances-Table',
            walk_oid='1.3.6.1.2.1.47.3.1',
            row_base='1',
            index_column='1',
            column_list=[
                'entity_compliance',
                'entity2_compliance',
            ],
            snmp_server=kwargs['snmp_server'],
        )
