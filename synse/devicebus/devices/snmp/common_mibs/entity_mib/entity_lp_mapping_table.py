#!/usr/bin/env python
""" Synse Entity MIB entity Logical to Physical entLPMappingTable.

    \\//
     \/apor IO

-------------------------------
Copyright (C) 2015-17  Vapor IO

This file is part of Synse.

Synse is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

Synse is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Synse.  If not, see <http://www.gnu.org/licenses/>.
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class EntityLPMappingTable(SnmpTable):
    """SNMP table specific to the Entity MIB."""

    def __init__(self, **kwargs):
        super(EntityLPMappingTable, self).__init__(
            table_name='Entity-MIB-Entity-LP-Mapping-Table',
            walk_oid='1.3.6.1.2.1.47.1.3.1',
            row_base='1',
            readable_column='1',
            column_list=[
                'index',
            ],
            snmp_server=kwargs['snmp_server'],
        )
