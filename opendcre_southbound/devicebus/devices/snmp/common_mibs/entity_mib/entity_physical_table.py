#!/usr/bin/env python
""" OpenDCRE Southbound Entity MIB entityPhysical entPhysicalTable.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class EntityPhysicalTable(SnmpTable):
    """SNMP table specific to the Entity MIB."""

    def __init__(self, **kwargs):

        super(EntityPhysicalTable, self).__init__(
            table_name='Entity-MIB-Entity-Physical-Table',
            walk_oid='1.3.6.1.2.1.47.1.1',
            row_base='1.1',
            readable_column='2',
            column_list=[
                'index',
                'description',
                'vendor_type',
                'contained_in',
                'class',
                'parent_relative_position',
                'name',
                'hardware_rev',
                'firmware_rev',
                'software_rev',
                'serial_number',
                'manufacturer_name',
                'model_name',
                'alias',
                'asset_id',
                'is_fru',
                'manufactured_date',
                'uris',
            ],
            snmp_server=kwargs['snmp_server'],
        )
