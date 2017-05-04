#!/usr/bin/env python
""" Synse UPS MIB upsOutputTable.

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

from ......devicebus.devices.snmp.snmp_table import SnmpTable

logger = logging.getLogger(__name__)


class UpsOutputTable(SnmpTable):
    """SNMP table specific to the UPS MIB."""

    def __init__(self, **kwargs):

        super(UpsOutputTable, self).__init__(
            table_name='UPS-MIB-UPS-Output-Table',
            walk_oid='1.3.6.1.2.1.33.1.4.4',
            row_base='1',
            readable_column='2',
            column_list=[
                'index',        # The MIB says that this is not accessible, but it's in the walk.
                'voltage',      # RMS Volts.
                'current',      # 0.1 RMS Amp.
                'power',        # Watts.
                'percent_load',
            ],
            snmp_server=kwargs['snmp_server'],
        )

    def get_scan_devices(self):
        """Gets a list of devices we return on a scan for this table."""
        scan_devices = []
        for row in self.rows:
            next_devices = self.get_scan_devices_public()
            for next_device in next_devices:
                # This needs to be in the private scan cache, but not public.
                next_device['snmp_row'] = row.to_scan_json()
                scan_devices.append(next_device)
        return scan_devices

    def get_scan_devices_public(self):
        """Get devices we return on a scan for this table."""
        scan_devices = []
        device_info = 'output{}'.format(self.snmp_server.get_next_output_power_id())
        device_types = {'voltage', 'current', 'power', 'percent_load'}
        for device_type in device_types:
            scan_device = {
                'device_id': self.snmp_server.get_next_device_id(),
                'device_info': device_info,
                'device_type': device_type,
            }
            scan_devices.append(scan_device)
        return scan_devices

    def get_row_power(self, row):
        """Given an SnmpRow row, translate it to a reading.
        :param row: The SnmpRow we read from the SNMP server."""
        logger.debug('UpsOutputTable.get_row_power')

        reading = row['power']
        if reading == 0:
            power_state = 'off'
        else:
            power_state = 'on'

        response_data = {
            'input_power': reading,     # This is where input power is a bug. Should be power.
            'over_current': False,
            'power_ok': True,
            'power_status': power_state,
        }
        return response_data

    def get_row_voltage(self, row):
        """Given an SnmpRow row, translate it to a reading.
        :param row: The SnmpRow we read from the SNMP server."""
        logger.debug('UpsOutputTable.get_row_voltage')
        response_data = {'health': 'ok', 'states': [], 'voltage': row['voltage']}
        return response_data
