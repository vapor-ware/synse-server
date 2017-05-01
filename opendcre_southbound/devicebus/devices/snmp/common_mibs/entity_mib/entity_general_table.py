#!/usr/bin/env python
""" OpenDCRE Southbound Entity MIB entity general.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class EntityGeneralTable(SnmpTable):
    """SNMP table specific to the Entity MIB. This is just OID
    .1.3.6.1.2.1.47.1.4.1.0, but it's simplest to treat everything as a table.
    """

    def __init__(self, **kwargs):

        super(EntityGeneralTable, self).__init__(
            table_name='Entity-MIB-Entity-General-Table',
            walk_oid='1.3.6.1.2.1.47.1.4',
            flattened_table=True,
            column_list=[
                'last_change_time',
            ],
            snmp_server=kwargs['snmp_server'],
        )
