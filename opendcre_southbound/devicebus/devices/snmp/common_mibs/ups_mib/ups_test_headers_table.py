#!/usr/bin/env python
""" OpenDCRE Southbound UPS MIB upsTest Headers Table.

    \\//
     \/apor IO
"""

from ......devicebus.devices.snmp.snmp_table import SnmpTable


class UpsTestHeadersTable(SnmpTable):
    """SNMP table specific to the UPS MIB."""

    def __init__(self, **kwargs):

        super(UpsTestHeadersTable, self).__init__(
            table_name='UPS-MIB-UPS-Test-Headers-Table',
            walk_oid='1.3.6.1.2.1.33.1.7',
            flattened_table=True,
            column_list=[
                'id',
                'spin_lock',
                'results_summary',
                'results_detail',
                'start_time',
                'elapsed_time',
            ],
            snmp_server=kwargs['snmp_server'],
        )

    # Column level constants.
    RESULTS_SUMMARY_DONE_PASS = 1
    RESULTS_SUMMARY_DONE_WARNING = 2
    RESULTS_SUMMARY_DONE_ERROR = 3
    RESULTS_SUMMARY_ABORTED = 4
    RESULTS_SUMMARY_IN_PROGRESS = 5
    RESULTS_SUMMARY_NO_TESTS_INITIATED = 6
