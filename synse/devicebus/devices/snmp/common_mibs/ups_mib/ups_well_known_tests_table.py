#!/usr/bin/env python
""" Synse UPS MIB upsAlarms Well Known Tests Table.

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


class UpsWellKnownTestsTable(SnmpTable):
    """SNMP table specific to the UPS MIB."""

    def __init__(self, **kwargs):

        super(UpsWellKnownTestsTable, self).__init__(
            table_name='UPS-MIB-UPS-Well-Known-Tests-Table',
            walk_oid='1.3.6.1.2.1.33.1.7.7',
            readable_column='1',
            column_list=[
                'no_tests_initiated',
                'abort_test_in_progress',
                'general_systems_test',
                'quick_battery_test',
                'deep_battery_calibration',
            ],
            snmp_server=kwargs['snmp_server'],
        )
