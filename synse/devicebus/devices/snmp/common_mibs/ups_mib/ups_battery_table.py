#!/usr/bin/env python
""" Synse UPS MIB upsBattery Table.

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


class UpsBatteryTable(SnmpTable):
    """SNMP table specific to the UPS MIB."""

    def __init__(self, **kwargs):

        super(UpsBatteryTable, self).__init__(
            table_name='UPS-MIB-UPS-Battery-Table',
            walk_oid='1.3.6.1.2.1.33.1.2',
            flattened_table=True,
            column_list=[
                'status',
                'seconds_on_battery',           # Zero if not on battery power.
                'estimated_minutes_remaining',
                'estimated_charge_remaining',   # Percentage.
                'voltage',                      # Units .1 VDC.
                'current',                      # Units .1 Amp DC.
                'temperature',                  # Units degrees C.
            ],
            snmp_server=kwargs['snmp_server'],
        )

    # Column level enum constants.
    # Status column.
    STATUS_UNKNOWN = 1
    STATUS_NORMAL = 2
    STATUS_LOW = 3
    STATUS_DEPLETED = 4

    @staticmethod
    def _get_device_status(status):
        """Get a string representation of the device status from the
        status column in this table.
        :returns: 'ok', 'low', 'depleted', or 'unknown'."""
        if status == UpsBatteryTable.STATUS_NORMAL:
            return 'ok'
        elif status == UpsBatteryTable.STATUS_LOW:
            return 'low'
        elif status == UpsBatteryTable.STATUS_DEPLETED:
            return 'depleted'
        return 'unknown'

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
        """Get a devices we return on a scan for this table."""
        scan_devices = []
        device_info = 'battery{}'.format(self.snmp_server.get_next_battery_id())

        # Other columns are not yet mapped to Synse device types.
        device_types = {'voltage', 'current', 'temperature'}
        for device_type in device_types:
            scan_device = {
                'device_id': self.snmp_server.get_next_device_id(),
                'device_info': device_info,
                'device_type': device_type,
            }
            scan_devices.append(scan_device)
        return scan_devices

    def get_row_temperature(self, row):
        """Given an SnmpRow row, translate it to a reading.
        :param row: The SnmpRow we read from the SNMP server."""
        logger.debug('UpsBatteryTable.get_row_temperature')
        reading = row['temperature']
        health = UpsBatteryTable._get_device_status(row['status'])
        response_data = {'health': health, 'states': [], 'temperature_c': reading}
        return response_data

    def get_row_voltage(self, row):
        """Given an SnmpRow row, translate it to a reading.
        :param row: The SnmpRow we read from the SNMP server."""
        logger.debug('UpsBatteryTable.get_row_voltage')
        # Look - No floating point math disasters.
        reading = float('{}.{}'.format(row['voltage'] / 10, row['voltage'] % 10))
        health = UpsBatteryTable._get_device_status(row['status'])
        response_data = {'health': health, 'states': [], 'voltage': reading}
        return response_data
