#!/usr/bin/env python
""" Synse TestTable1 LED table.

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
from synse.devicebus.devices.snmp.snmp_table import SnmpTable


logger = logging.getLogger(__name__)


class LedTable(SnmpTable):
    """ SNMP table specific to the test variable table.
    """

    def __init__(self, **kwargs):

        super(LedTable, self).__init__(
            table_name='Synse-TestDevice1-Led-Table',
            walk_oid='1.3.6.1.4.1.61439.1.4.3',
            row_base='2.1',
            index_column='1',
            column_list=[
                'index',
                'id',
                'name',
                'state',
                'blink_state',
                'color',
            ],
            snmp_server=kwargs['snmp_server'],
        )

    def get_scan_devices(self):
        """ Gets a list of devices we return on a scan for this table.

        Returns:
            list: list of devices found from scan.
        """
        scan_devices = []
        for row in self.rows:
            scan_device = self.get_scan_device_public()
            # This needs to be in the private scan cache, but not public.
            scan_device['snmp_row'] = row.to_scan_json()
            scan_devices.append(scan_device)
        return scan_devices

    def get_scan_device_public(self):
        """ Get a single device we return on a scan for this table.

        Returns:
            dict: single device from scan.
        """
        scan_device = {
            'device_id': self.snmp_server.get_next_device_id(),
            'device_info': 'led',
            'device_type': 'led',
        }
        return scan_device
