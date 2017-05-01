#!/usr/bin/env python
""" OpenDCRE Southbound Entity MIB entity GroupsTable.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class EntityGroupsTable(SnmpTable):
    """SNMP table specific to the Entity MIB. This is just OIDs under
    1.3.6.1.2.1.47.3.2, but it's simplest to treat everything as a table.
    We do not have real data  for these OIDs so this is currently
    untested."""

    def __init__(self, **kwargs):

        super(EntityGroupsTable, self).__init__(
            table_name='Entity-MIB-Entity-Groups-Table',
            walk_oid='1.3.6.1.2.1.47.3.2',
            index_column='1',
            column_list=[
                'physical',
                'logical',
                'mapping',
                'general',
                'notifications',
                'physical2',
                'logical2',
            ],
            snmp_server=kwargs['snmp_server'],
        )
