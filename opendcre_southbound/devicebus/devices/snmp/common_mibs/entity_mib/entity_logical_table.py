#!/usr/bin/env python
""" OpenDCRE Southbound Entity MIB entityLogical entLogicalTable.

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


class EntityLogicalTable(SnmpTable):
    """SNMP table specific to the Entity MIB."""

    def __init__(self, **kwargs):

        super(EntityLogicalTable, self).__init__(
            table_name='Entity-MIB-Entity-Logical-Table',
            walk_oid='1.3.6.1.2.1.47.1.2',
            row_base='1.1',
            readable_column='2',
            column_list=[
                'index',
                'description',
                'type',
                'community',
                'transport_address',
                'transport_domain',
                'context_engine_id',
                'context_name',
            ],
            snmp_server=kwargs['snmp_server'],
        )
