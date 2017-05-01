#!/usr/bin/env python
""" OpenDCRE Southbound Entity MIB entitySensor entSensorGroupsTable.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class EntitySensorGroupsTable(SnmpTable):
    """SNMP table specific to the Entity Sensor MIB. We have no real data
    on these OIDs, so this is untested."""

    def __init__(self, **kwargs):

        super(EntitySensorGroupsTable, self).__init__(
            table_name='Entity-MIB-Entity-Physical-Sensor-Groups-Table',
            walk_oid='1.3.6.1.2.1.99.3.2',
            index_column='1',
            column_list=[
                'value_group',
            ],
            snmp_server=kwargs['snmp_server'],
        )
