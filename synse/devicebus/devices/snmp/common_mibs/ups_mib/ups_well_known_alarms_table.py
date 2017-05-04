#!/usr/bin/env python
""" Synse UPS MIB upsAlarms Well Known Alarms Table.

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


class UpsWellKnownAlarmsTable(SnmpTable):
    """ SNMP table specific to the UPS MIB.
    """

    def __init__(self, **kwargs):

        super(UpsWellKnownAlarmsTable, self).__init__(
            table_name='UPS-MIB-UPS-Well-Known-Alarms-Table',
            walk_oid='1.3.6.1.2.1.33.1.6.3',
            readable_column='1',
            column_list=[
                'battery_bad',
                'on_battery',
                'low_battery',
                'depleted_battery',
                'temp_bad',
                'input_bad',
                'output_bad',
                'output_overload',
                'on_bypass',
                'bypass_bad',
                'output_off_as_requested',
                'charger_failed',
                'ups_output_off',
                'ups_system_off',
                'fan_failure',
                'fuse_failure',
                'general_fault',
                'diagnostic_test_failed',
                'communications_lost',
                'awaiting_power',
                'shutdown_pending',
                'shutdown_imminent',
                'test_in_progress',
            ],
            snmp_server=kwargs['snmp_server'],
        )
