#!/usr/bin/env python
""" OpenDCRE Southbound UPS MIB upsControl Table.

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


class UpsControlTable(SnmpTable):
    """SNMP table specific to the UPS MIB."""

    def __init__(self, **kwargs):

        super(UpsControlTable, self).__init__(
            table_name='UPS-MIB-UPS-Control-Table',
            walk_oid='1.3.6.1.2.1.33.1.8',
            flattened_table=True,
            column_list=[
                'shutdown_type',
                'shutdown_after_delay',     # Seconds
                'startup_after_delay',      # Seconds
                'reboot_with_duration',     # Seconds
                'auto_restart',
                # The walk data has two extra columns here, but they're
                # not defined in the RFC or here http://www.oidview.com/mibs/0/UPS-MIB.html
            ],
            snmp_server=kwargs['snmp_server'],
        )

    # Column level constants.
    SHUTDOWN_TYPE_OUTPUT = 1
    SHUTDOWN_TYPE_SYSTEM = 2

    AUTO_RESTART_ON = 1
    AUTO_RESTART_OFF = 2
