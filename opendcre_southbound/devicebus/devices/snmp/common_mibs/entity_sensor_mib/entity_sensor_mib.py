#!/usr/bin/env python
""" OpenDCRE Southbound Base class for specific SNMP Entity Sensor MIB
implementations.

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

import logging

from ...snmp_mib import SnmpMib

from .entity_physical_sensor_table import EntityPhysicalSensorTable
from .entity_sensor_compliances_table import EntitySensorCompliancesTable
from .entity_sensor_groups import EntitySensorGroupsTable

logger = logging.getLogger(__name__)


class EntitySensorMib(SnmpMib):
    """Container for all SNMP tables defined in the Entity Sensor MIB (rfc3433)."""

    def __init__(self, snmp_server):
        super(EntitySensorMib, self).__init__()
        self.name = 'Entity Sensor Mib'

        # Define each table in the MIB.
        self.entity_physical_sensor_table = EntityPhysicalSensorTable(snmp_server=snmp_server)
        self.entity_sensor_conformance_table = EntitySensorCompliancesTable(snmp_server=snmp_server)
        self.entity_sensor_groups_table = EntitySensorGroupsTable(snmp_server=snmp_server)

        # Define a set of all tables to perform load and unload operations.
        self.tables = {
            self.entity_physical_sensor_table,
            self.entity_sensor_conformance_table,
            self.entity_sensor_groups_table,
        }
