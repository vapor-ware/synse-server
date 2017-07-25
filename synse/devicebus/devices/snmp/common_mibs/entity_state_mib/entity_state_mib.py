#!/usr/bin/env python
""" Synse Base class for specific SNMP Entity State MIB implementations.

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

from ...snmp_mib import SnmpMib
from .entity_state_conformance import EntityStateConformanceTable
from .entity_state_groups import EntityStateGroupsTable
from .entity_state_objects import EntityStateObjectsTable


class EntityStateMib(SnmpMib):
    """ Container for all SNMP tables defined in the Entity State MIB (rfc4268).
    """

    def __init__(self, snmp_server):
        super(EntityStateMib, self).__init__()
        self.name = 'Entity State Mib'

        # Define each table in the MIB.
        self.entity_state_objects_table = EntityStateObjectsTable(snmp_server=snmp_server)
        self.entity_state_conformance_table = EntityStateConformanceTable(snmp_server=snmp_server)
        self.entity_state_groups_table = EntityStateGroupsTable(snmp_server=snmp_server)

        # Define a set of all tables to perform load and unload operations.
        self.tables = {
            self.entity_state_objects_table,
            self.entity_state_conformance_table,
            self.entity_state_groups_table,
        }
