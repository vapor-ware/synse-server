#!/usr/bin/env python
""" OpenDCRE Southbound UPS MIB upsConfig Table.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class UpsConfigTable(SnmpTable):
    """SNMP table specific to the UPS MIB."""

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
