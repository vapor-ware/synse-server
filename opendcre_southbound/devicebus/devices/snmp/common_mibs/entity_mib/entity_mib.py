#!/usr/bin/env python
""" OpenDCRE Southbound Base class for specific SNMP Entity MIB implementations.

    \\//
     \/apor IO
"""

import logging

from ...snmp_mib import SnmpMib

from .entity_physical_table import EntityPhysicalTable
from .entity_logical_table import EntityLogicalTable
from .entity_lp_mapping_table import EntityLPMappingTable
from .entity_alias_mapping_table import EntityAliasMappingTable
from .entity_physical_contains_table import EntityPhysicalContainsTable
from .entity_general_table import EntityGeneralTable
from .entity_compliances_table import EntityCompliancesTable
from .entity_groups_table import EntityGroupsTable


logger = logging.getLogger(__name__)


class EntityMib(SnmpMib):
    """Container for all SNMP tables defined in the Entity MIB (rfc4133)."""

    def __init__(self, snmp_server):
        super(EntityMib, self).__init__()
        self.name = 'Entity Mib'

        # Define each table in the MIB.
        self.entity_physical_table = EntityPhysicalTable(snmp_server=snmp_server)
        self.entity_logical_table = EntityLogicalTable(snmp_server=snmp_server)
        self.entity_lp_mapping_table = EntityLPMappingTable(snmp_server=snmp_server)
        self.entity_alias_mapping_table = EntityAliasMappingTable(snmp_server=snmp_server)
        self.entity_physical_contains_table = EntityPhysicalContainsTable(snmp_server=snmp_server)
        self.entity_general_table = EntityGeneralTable(snmp_server=snmp_server)
        self.entity_compliances_table = EntityCompliancesTable(snmp_server=snmp_server)
        self.entity_groups_table = EntityGroupsTable(snmp_server=snmp_server)

        # Define a set of all tables to perform load and unload operations.
        self.tables = {
            self.entity_physical_table,
            self.entity_logical_table,
            self.entity_lp_mapping_table,
            self.entity_alias_mapping_table,
            self.entity_physical_contains_table,
            self.entity_general_table,
            self.entity_compliances_table,
            self.entity_groups_table,
        }
