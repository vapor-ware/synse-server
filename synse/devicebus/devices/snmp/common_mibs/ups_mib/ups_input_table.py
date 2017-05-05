#!/usr/bin/env python
""" Synse UPS MIB upsInputTable.

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


class UpsInputTable(SnmpTable):
    """ SNMP table specific to the UPS MIB.
    """

    def __init__(self, **kwargs):

        super(UpsInputTable, self).__init__(
            table_name='UPS-MIB-UPS-Input-Table',
            walk_oid='1.3.6.1.2.1.33.1.3.3',
            row_base='1',
            readable_column='2',
            column_list=[
                'index',        # The MIB says that this is not accessible, but it's in the walk.
                'frequency',    # .1 Hertz
                'current',      # .1 RMS Amp
                'voltage',      # RMS Volts
                'true_power',   # Down with False Power! (Watts)
            ],
            snmp_server=kwargs['snmp_server'],
        )

    def get_scan_devices(self):
        """ Gets a list of devices we return on a scan for this table.

        Returns:
            list: devices found from a scan.
        """
        scan_devices = []
        for row in self.rows:
            next_devices = self.get_scan_devices_public()
            for next_device in next_devices:
                # This needs to be in the private scan cache, but not public.
                next_device['snmp_row'] = row.to_scan_json()
                scan_devices.append(next_device)
        return scan_devices

    def get_scan_devices_public(self):
        """ Get devices we return on a scan for this table.

        Returns:
            list: devices found from a scan.
        """
        scan_devices = []
        device_info = 'input{}'.format(self.snmp_server.get_next_input_power_id())
        device_types = {'frequency', 'voltage', 'current', 'power'}
        for device_type in device_types:
            scan_device = {
                'device_id': self.snmp_server.get_next_device_id(),
                'device_info': device_info,
                'device_type': device_type,
            }
            scan_devices.append(scan_device)
        return scan_devices

    def get_row_power(self, row):
        """ Given an SnmpRow row, translate it to a reading.

        Args:
            row (SnmpRow): The SnmpRow we read from the SNMP server.

        Returns:
            dict: the response data for the power reading.
        """
        logger.debug('UpsInputTable.get_row_power')

        reading = row['true_power']
        if reading == 0:
            power_state = 'off'
        else:
            power_state = 'on'

        response_data = {
            'input_power': reading,
            'over_current': False,
            'power_ok': True,
            'power_status': power_state,
        }
        return response_data

    def get_row_voltage(self, row):
        """ Given an SnmpRow row, translate it to a reading.

        Args:
            row (SnmpRow): The SnmpRow we read from the SNMP server.

        Returns:
            dict: the response data for the voltage reading.
        """
        logger.debug('UpsInputTable.get_row_voltage')
        response_data = {'health': 'ok', 'states': [], 'voltage': row['voltage']}
        return response_data
