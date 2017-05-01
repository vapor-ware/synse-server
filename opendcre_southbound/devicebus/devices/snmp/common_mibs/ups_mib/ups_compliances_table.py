#!/usr/bin/env python
""" OpenDCRE Southbound UPS MIB upsCompliances Table.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class UpsCompliancesTable(SnmpTable):
    """SNMP table specific to the UPS MIB."""

    def __init__(self, **kwargs):

        super(UpsCompliancesTable, self).__init__(
            table_name='UPS-MIB-UPS-Compliances-Table',
            walk_oid='1.3.6.1.2.1.33.3.1',
            column_list=[
                'subset_compliance',
                'basic_compliance',
                'full_compliance',
            ],
            snmp_server=kwargs['snmp_server'],
        )
