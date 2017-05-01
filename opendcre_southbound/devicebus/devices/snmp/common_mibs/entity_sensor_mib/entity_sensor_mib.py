#!/usr/bin/env python
""" OpenDCRE Southbound Base class for specific SNMP Entity Sensor MIB
implementations.

    \\//
     \/apor IO
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
