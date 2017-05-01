#!/usr/bin/env python
""" OpenDCRE Southbound UPS MIB upsAlarms Headers Table.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class UpsAlarmsHeadersTable(SnmpTable):
    """SNMP table specific to the UPS MIB."""

    def __init__(self, **kwargs):

        super(UpsAlarmsHeadersTable, self).__init__(
            table_name='UPS-MIB-UPS-Alarms-Headers-Table',
            walk_oid='1.3.6.1.2.1.33.1.6',
            flattened_table=True,
            column_list=[
                'present',  # The present number of active alarm conditions.
            ],
            snmp_server=kwargs['snmp_server'],
        )
