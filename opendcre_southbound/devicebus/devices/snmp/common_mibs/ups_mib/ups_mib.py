#!/usr/bin/env python
""" OpenDCRE Southbound Base class for specific SNMP UPS MIB implementations.

    \\//
     \/apor IO
"""

from ...snmp_mib import SnmpMib

from .ups_identity_table import UpsIdentityTable
from .ups_battery_table import UpsBatteryTable
from .ups_input_line_headers_table import UpsInputHeadersTable
from .ups_input_table import UpsInputTable
from .ups_output_headers_table import UpsOutputHeadersTable
from .ups_output_table import UpsOutputTable
from .ups_bypass_headers_table import UpsBypassHeadersTable
from .ups_bypass_table import UpsBypassTable
from .ups_alarms_headers_table import UpsAlarmsHeadersTable
from .ups_alarms_table import UpsAlarmsTable
from .ups_well_known_alarms_table import UpsWellKnownAlarmsTable
from .ups_test_headers_table import UpsTestHeadersTable
from .ups_well_known_tests_table import UpsWellKnownTestsTable
from .ups_control_table import UpsControlTable
from .ups_config_table import UpsConfigTable
from .ups_compliances_table import UpsCompliancesTable
from .ups_subset_groups_table import UpsSubsetGroupsTable
from .ups_basic_groups_table import UpsBasicGroupsTable
from .ups_full_groups_table import UpsFullGroupsTable


class UpsMib(SnmpMib):
    """Container for all SNMP tables defined in the UPS MIB (rfc1628)."""

    def __init__(self, snmp_server):
        super(UpsMib, self).__init__()
        self.name = 'Ups Mib'

        # Define each table in the MIB.
        self.ups_identity_table = UpsIdentityTable(snmp_server=snmp_server)
        self.ups_battery_table = UpsBatteryTable(snmp_server=snmp_server)
        self.ups_input_line_headers_table = UpsInputHeadersTable(snmp_server=snmp_server)
        self.ups_input_table = UpsInputTable(snmp_server=snmp_server)
        self.ups_output_headers_table = UpsOutputHeadersTable(snmp_server=snmp_server)
        self.ups_output_table = UpsOutputTable(snmp_server=snmp_server)
        self.ups_bypass_headers_table = UpsBypassHeadersTable(snmp_server=snmp_server)
        self.ups_bypass_table = UpsBypassTable(snmp_server=snmp_server)
        self.ups_alarms_headers_table = UpsAlarmsHeadersTable(snmp_server=snmp_server)
        self.ups_alarms_table = UpsAlarmsTable(snmp_server=snmp_server)
        self.ups_well_known_alarms_table = UpsWellKnownAlarmsTable(snmp_server=snmp_server)
        self.ups_test_headers_table = UpsTestHeadersTable(snmp_server=snmp_server)
        self.ups_well_known_tests_table = UpsWellKnownTestsTable(snmp_server=snmp_server)
        self.ups_control_table = UpsControlTable(snmp_server=snmp_server)
        self.ups_config_table = UpsConfigTable(snmp_server=snmp_server)
        self.ups_compliances_table = UpsCompliancesTable(snmp_server=snmp_server)
        self.ups_subset_groups_table = UpsSubsetGroupsTable(snmp_server=snmp_server)
        self.ups_basic_groups_table = UpsBasicGroupsTable(snmp_server=snmp_server)
        self.ups_full_groups_table = UpsFullGroupsTable(snmp_server=snmp_server)

        # Define a set of all tables to perform load and unload operations.
        self.tables = {
            self.ups_identity_table,
            self.ups_battery_table,
            self.ups_input_line_headers_table,
            self.ups_input_table,
            self.ups_output_headers_table,
            self.ups_output_table,
            self.ups_bypass_headers_table,
            self.ups_bypass_table,
            self.ups_alarms_headers_table,
            self.ups_alarms_table,
            self.ups_well_known_alarms_table,
            self.ups_test_headers_table,
            self.ups_well_known_tests_table,
            self.ups_control_table,
            self.ups_config_table,
            self.ups_compliances_table,
            self.ups_subset_groups_table,
            self.ups_basic_groups_table,
            self.ups_full_groups_table,
        }
