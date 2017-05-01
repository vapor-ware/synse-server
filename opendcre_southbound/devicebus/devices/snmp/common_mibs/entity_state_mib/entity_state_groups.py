#!/usr/bin/env python
""" OpenDCRE Southbound Entity MIB entityState entStateGroupsTable.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class EntityStateGroupsTable(SnmpTable):
    """SNMP table specific to the Entity State MIB. We have no data from Rittal
    on these OIDs so this is untested."""

    def __init__(self, **kwargs):

        super(EntityStateGroupsTable, self).__init__(
            table_name='Entity-MIB-Entity-State-Groups-Table',
            walk_oid='1.3.6.1.2.1.131.2.2',
            index_column='1',
            column_list=[
                'group',
                'notifications_group',
            ],
            snmp_server=kwargs['snmp_server'],
        )
