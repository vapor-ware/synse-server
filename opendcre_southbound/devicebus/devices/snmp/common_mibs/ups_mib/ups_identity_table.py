#!/usr/bin/env python
""" OpenDCRE Southbound UPS MIB upsIdent Table.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class UpsIdentityTable(SnmpTable):
    """SNMP table specific to the UPS MIB."""

    def __init__(self, **kwargs):

        super(UpsIdentityTable, self).__init__(
            table_name='UPS-MIB-UPS-Identity-Table',
            walk_oid='1.3.6.1.2.1.33.1.1',
            flattened_table=True,
            column_list=[
                'manufacturer',
                'model',
                'ups_software_version',
                'agent_software_version',
                'name',
                'attached_devices',
            ],
            snmp_server=kwargs['snmp_server'],
        )
