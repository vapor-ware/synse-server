#!/usr/bin/env python
""" OpenDCRE Southbound OpenDCRE TestTable1 led table.

    \\//
     \/apor IO
"""

import logging
from opendcre_southbound.devicebus.devices.snmp.snmp_table import SnmpTable


logger = logging.getLogger(__name__)


class LedTable(SnmpTable):
    """SNMP table specific to Rittal RiZone variable table."""

    def __init__(self, **kwargs):

        super(LedTable, self).__init__(
            table_name='OpenDcre-TestDevice1-Led-Table',
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
            'device_info': 'led',
            'device_type': 'led',
        }
        return scan_device
