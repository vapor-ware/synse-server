#!/usr/bin/env python
""" OpenDCRE Southbound OpenDCRE TestTable1 led table.

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
from opendcre_southbound.devicebus.devices.snmp.snmp_table import SnmpTable


logger = logging.getLogger(__name__)


class PowerTable(SnmpTable):
    """SNMP table specific to the test variable table."""

    def __init__(self, **kwargs):

        super(PowerTable, self).__init__(
            table_name='OpenDcre-TestDevice1-Power-Table',
            walk_oid='1.3.6.1.4.1.61439.1.4.1',
            row_base='2.1',
            index_column='1',
            column_list=[
                'index',
                'id',
                'name',
                'state',
                'voltage',
            ],
            snmp_server=kwargs['snmp_server'],
        )

    def get_scan_devices(self):
        """Gets a list of devices we return on a scan for this table."""
        scan_devices = []
        for row in self.rows:
            scan_device = self.get_scan_device_public()
            # This needs to be in the private scan cache, but not public.
            scan_device['snmp_row'] = row.to_scan_json()
            scan_devices.append(scan_device)
        return scan_devices

    def get_scan_device_public(self):
        """Get a single device we return on a scan for this table."""
        scan_device = {
            'device_id': self.snmp_server.get_next_device_id(),
            'device_info': 'power',
            'device_type': 'power'
        }
        return scan_device

    # TODO: This needs to be addressed in the interface cleanup.
    def get_row_reading(self, row, device_type_string):
        """Given an SnmpRow row, translate it to a reading.
        :param row: The SnmpRow we read from the SNMP server.
        :param device_type_string: Unused."""
        logger.debug('PowerTable.get_row_reading')

        reading = row['voltage']
        response_data = {'health': 'ok', 'states': [], 'voltage': reading}
        return response_data
