#!/usr/bin/env python
""" OpenDCRE Southbound UPS MIB upsAlarmsTable.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class UpsAlarmsTable(SnmpTable):
    """SNMP table specific to the UPS MIB."""

    def __init__(self, **kwargs):

        super(UpsAlarmsTable, self).__init__(
            table_name='UPS-MIB-UPS-Alarms-Table',
            walk_oid='1.3.6.1.2.1.33.1.6.2',
            row_base='1',
            readable_column='2',
            column_list=[
                'index',
                'description',
                'time',
            ],
            snmp_server=kwargs['snmp_server'],
        )
