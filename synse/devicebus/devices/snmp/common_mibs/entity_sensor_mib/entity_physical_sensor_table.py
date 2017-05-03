#!/usr/bin/env python
""" Synse Entity MIB entitySensor entPhySensorTable.

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
from ......errors import CommandNotSupported

logger = logging.getLogger(__name__)


class EntityPhysicalSensorTable(SnmpTable):
    """SNMP table specific to the Entity Sensor MIB."""

    def __init__(self, **kwargs):

        super(EntityPhysicalSensorTable, self).__init__(
            table_name='Entity-MIB-Entity-Physical-Sensor-Table',
            walk_oid='1.3.6.1.2.1.99.1',
            row_base='1.1',
            readable_column='1',
            column_list=[
                'type',
                'scale',
                'precision',
                'value',
                'operational_status',
                'units_display',
                'timestamp',
                'update_rate',
            ],
            snmp_server=kwargs['snmp_server'],
        )

    # Column level enum constants.
    # Type column.
    TYPE_OTHER = 1
    TYPE_UNKNOWN = 2
    TYPE_VOLTS_AC = 3
    TYPE_VOLTS_DC = 4
    TYPE_AMPERES = 5
    TYPE_WATTS = 6
    TYPE_HERTZ = 7
    TYPE_CELSIUS = 8
    TYPE_PERCENT_RH = 9     # Percent relative humidity
    TYPE_RPM = 10
    TYPE_CMM = 11           # Cubic Meters per Minute (flow)
    TYPE_TRUTH_VALUE = 12   # true (1), false (2)

    # Scale column.
    SCALE_YOCTO = 1
    SCALE_ZEPTO = 2
    SCALE_ATTO = 3
    SCALE_FEMTO = 4
    SCALE_PICO = 5
    SCALE_NANO = 6
    SCALE_MICRO = 7
    SCALE_MILLI = 8
    SCALE_UNITS = 9
    SCALE_KILO = 10
    SCALE_MEGA = 11
    SCALE_GIGA = 12
    SCALE_TERA = 13
    SCALE_PETA = 14
    SCALE_EXA = 15
    SCALE_ZETTA = 16
    SCALE_YOTTA = 17

    # Operational Status column.
    STATUS_OK = 1
    STATUS_UNAVAILABLE = 2
    STATUS_NONOPERATIONAL = 3

    # Map of scale to exponent.
    SCALE_TO_EXPONENT = {
        SCALE_YOCTO: -24,
        SCALE_ZEPTO: -21,
        SCALE_ATTO: -18,
        SCALE_FEMTO: -15,
        SCALE_PICO: -12,
        SCALE_NANO: -9,
        SCALE_MICRO: -6,
        SCALE_MILLI: -3,
        SCALE_UNITS: 0,
        SCALE_KILO: 3,
        SCALE_MEGA: 6,
        SCALE_GIGA: 9,
        SCALE_TERA: 12,
        SCALE_PETA: 15,
        SCALE_EXA: 18,
        SCALE_ZETTA: 21,
        SCALE_YOTTA: 24,
    }

    @staticmethod
    def _get_device_status(operational_status):
        """Get a string representation of the device status from the
        operational_status column in this table.
        :returns: 'ok' on success, else failure."""
        if operational_status == EntityPhysicalSensorTable.STATUS_OK:
            return 'ok'
        elif operational_status == EntityPhysicalSensorTable.STATUS_NONOPERATIONAL:
            return 'nonoperational'
        return 'unavailable'

    @staticmethod
    def _get_device_type(sensor_type):
        """:param sensor_type: The sensor type in the format of this table.
        :returns: The corresponding Synse device type."""

        # TODO: Localization for strings.

        # Other and unknown are not device types supported by Synse.
        # Not clear what device type a truth value might be.
        if sensor_type <= EntityPhysicalSensorTable.TYPE_UNKNOWN \
                or sensor_type >= EntityPhysicalSensorTable.TYPE_TRUTH_VALUE:
            return None

        elif EntityPhysicalSensorTable.TYPE_VOLTS_AC <= sensor_type \
                <= EntityPhysicalSensorTable.TYPE_VOLTS_DC:
            device_type = 'voltage'

        elif sensor_type == EntityPhysicalSensorTable.TYPE_AMPERES:
            device_type = 'current'

        elif sensor_type == EntityPhysicalSensorTable.TYPE_WATTS:
            device_type = 'power'

        elif sensor_type == EntityPhysicalSensorTable.TYPE_HERTZ:
            device_type = 'frequency'

        elif sensor_type == EntityPhysicalSensorTable.TYPE_CELSIUS:
            device_type = 'temperature'

        elif sensor_type == EntityPhysicalSensorTable.TYPE_PERCENT_RH:
            device_type = 'humidity'

        elif sensor_type == EntityPhysicalSensorTable.TYPE_RPM:
            device_type = 'fan_speed'   # The best we have.

        elif sensor_type == EntityPhysicalSensorTable.TYPE_CMM:
            # TBD: We will have airflow sensors soon. Flow may be preferable
            # over airflow since it may not be air (Chiller pump, etc).
            device_type = 'flow'

        else:
            return None

        return device_type

    @staticmethod
    def _get_row_reading(row):
        """Get the measurement from the row as a float. Raise ValueError on
        error."""
        logger.debug('Getting reading for row:')
        row.dump()
        operational_status = EntityPhysicalSensorTable._get_device_status(
            row['operational_status'])
        if operational_status != 'ok':
            raise ValueError('Device status {}.'.format(operational_status))

        # Deliberately ignoring precision for now.
        # The walk contains data of 20300, scale milli, precision 1.
        # This seems like it should read 20.3 rather than 20.
        # (Value has more precision than the precision column.)
        reading = float(row['value'])
        exponent = EntityPhysicalSensorTable.SCALE_TO_EXPONENT[row['scale']]
        reading *= 10 ** exponent
        return reading

    def get_scan_device_public(self, sensor_type):
        """Get a single device we return on a scan for this table.
        :param sensor_type: From the type enum above.
        :returns: Device information for a scan if the device type is supported
         or can be supported in Synse, else None."""
        device_type = EntityPhysicalSensorTable._get_device_type(sensor_type)
        if device_type is None:
            return None

        scan_device = {
            'device_id': self.snmp_server.get_next_device_id(),
            'device_info': device_type,
            'device_type': device_type,
        }
        return scan_device

    def get_scan_devices(self):
        """Gets a list of devices we return on a scan for this table."""
        scan_devices = []
        for row in self.rows:
            scan_device = self.get_scan_device_public(row['type'])
            if scan_device is not None:
                # This needs to be in the private scan cache, but not public.
                scan_device['snmp_row'] = row.to_scan_json()
                scan_devices.append(scan_device)
        return scan_devices

    def get_row_power(self, row):
        """Given an SnmpRow row, translate it to a reading.
        :param row: The SnmpRow we read from the SNMP server."""
        logger.debug('EntityPhysicalSensorTable.get_row_power')

        # TODO: Localization
        device_type = EntityPhysicalSensorTable._get_device_type(row['type'])
        if device_type is None:
            device_type = 'unknown'

        if device_type != 'power':
            raise CommandNotSupported(
                'Wrong sensor type. Request to read {}, but this sensor reads {}.'.format(
                    'power', device_type))

        reading = EntityPhysicalSensorTable._get_row_reading(row)
        if reading == 0:
            power_state = 'off'
        else:
            power_state = 'on'

        response_data = {
            'input_power': reading,    # TODO: This is where input_power is a bug. It should just be power.
            'over_current': False,
            'power_ok': True,
            'power_status': power_state,
        }

        return response_data

    def get_row_temperature(self, row):
        """Given an SnmpRow row, translate it to a reading.
        :param row: The SnmpRow we read from the SNMP server."""
        logger.debug('EntityPhysicalSensorTable.get_row_temperature')

        # TODO: Localization
        device_type = EntityPhysicalSensorTable._get_device_type(row['type'])
        if device_type is None:
            device_type = 'unknown'

        if device_type != 'temperature':
            raise CommandNotSupported(
                'Wrong sensor type. Request to read {}, but this sensor reads {}.'.format(
                    'temperature', device_type))

        reading = EntityPhysicalSensorTable._get_row_reading(row)
        response_data = {'health': 'ok', 'states': [], 'temperature_c': reading}
        return response_data

    def get_row_voltage(self, row):
        """Given an SnmpRow row, translate it to a reading.
        :param row: The SnmpRow we read from the SNMP server."""
        logger.debug('EntityPhysicalSensorTable.get_row_voltage')

        # TODO: Localization
        device_type = EntityPhysicalSensorTable._get_device_type(row['type'])
        if device_type is None:
            device_type = 'unknown'

        if device_type != 'voltage':
            raise CommandNotSupported(
                'Wrong sensor type. Request to read {}, but this sensor reads {}.'.format(
                    'voltage', device_type))

        reading = EntityPhysicalSensorTable._get_row_reading(row)
        response_data = {'health': 'ok', 'states': [], 'voltage': reading}
        return response_data
