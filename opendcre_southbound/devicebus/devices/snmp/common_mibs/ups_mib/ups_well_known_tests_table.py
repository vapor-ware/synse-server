#!/usr/bin/env python
""" OpenDCRE Southbound UPS MIB upsAlarms Well Known Tests Table.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class UpsWellKnownTestsTable(SnmpTable):
    """SNMP table specific to the UPS MIB."""

    def __init__(self, **kwargs):

        super(UpsWellKnownTestsTable, self).__init__(
            table_name='UPS-MIB-UPS-Well-Known-Tests-Table',
            walk_oid='1.3.6.1.2.1.33.1.7.7',
            readable_column='1',
            column_list=[
                'no_tests_initiated',
                'abort_test_in_progress',
                'general_systems_test',
                'quick_battery_test',
                'deep_battery_calibration',
            ],
            snmp_server=kwargs['snmp_server'],
        )
