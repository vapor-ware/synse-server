#!/usr/bin/env python
""" OpenDCRE Southbound OpenDCRE TestTable1 fan table.

    \\//
     \/apor IO
"""

import logging
from opendcre_southbound.devicebus.devices.snmp.snmp_table import SnmpTable


logger = logging.getLogger(__name__)


class FanTable(SnmpTable):
    """SNMP table specific to the test variable table."""

    def __init__(self, **kwargs):

        super(FanTable, self).__init__(
            table_name='OpenDcre-TestDevice1-Fan-Table',
            walk_oid='1.3.6.1.4.1.61439.1.4.2',
            row_base='2.1',
            index_column='1',
            column_list=[
                'index',
                'id',
                'name',
                'rpm',
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
            'device_info': 'fan_speed',
            'device_type': 'fan_speed'
        }
        return scan_device

    def get_row_reading(self, row, device_type_string):
        """Given an SnmpRow row, translate it to a reading.
        :param row: The SnmpRow we read from the SNMP server.
        :param device_type_string: Unused."""
        logger.debug('FanTable.get_row_reading')

        reading = row['rpm']

        response_data = {'health': 'ok', 'states': [], 'speed_rpm': reading}
        return response_data
