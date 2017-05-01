#!/usr/bin/env python
""" OpenDCRE Southbound Entity MIB entitySensor entSensorCompliancesTable.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class EntitySensorCompliancesTable(SnmpTable):
    """SNMP table specific to the Entity Sensor MIB. We have no data from
    Rittal for these OIDs so this is not tested."""

    def __init__(self, **kwargs):

        super(EntitySensorCompliancesTable, self).__init__(
            table_name='Entity-MIB-Entity-Physical-Sensor-Compliances-Table',
            walk_oid='1.3.6.1.2.1.99.3.1',
            row_base='1',
            index_column='1',
            column_list=[
                'compliance',
            ],
            snmp_server=kwargs['snmp_server'],
        )
