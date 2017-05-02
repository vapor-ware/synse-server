#!/usr/bin/env python
""" OpenDCRE Southbound Base class for specific SNMP Entity State MIB
implementations.

    \\//
     \/apor IO
"""

from ...snmp_mib import SnmpMib

from .entity_state_objects import EntityStateObjectsTable
from .entity_state_conformance import EntityStateConformanceTable
from .entity_state_groups import EntityStateGroupsTable


class EntityStateMib(SnmpMib):
    """Container for all SNMP tables defined in the Entity State MIB (rfc4268)."""

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
