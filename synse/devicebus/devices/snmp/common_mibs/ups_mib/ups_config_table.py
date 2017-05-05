#!/usr/bin/env python
""" Synse UPS MIB upsConfig Table.

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


class UpsConfigTable(SnmpTable):
    """ SNMP table specific to the UPS MIB.
    """

    def __init__(self, **kwargs):

        super(UpsConfigTable, self).__init__(
            table_name='UPS-MIB-UPS-Config-Table',
            walk_oid='1.3.6.1.2.1.33.1.9',
            flattened_table=True,
            column_list=[
                'input_voltage',                # RMS Volts.
                'input_frequency',              # 0.1 Hertz.
                'output_voltage',               # RMS Volts.
                'output_frequency',             # 0.1 Hertz.
                'output_va',                    # Volt Amps.
                'output_power',                 # Watts.
                'low_battery_time',             # Minutes.
                'audible_status',
                'low_voltage_transfer_point',   # RMS Volts.
                'high_voltage_transfer_point',  # RMS Volts.
            ],
            snmp_server=kwargs['snmp_server'],
        )

    # Column level constants.
    AUDIBLE_STATUS_DISABLED = 1
    AUDIBLE_STATUS_ENABLED = 2
    AUDIBLE_STATUS_MUTED = 3
