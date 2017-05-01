#!/usr/bin/env python
""" OpenDCRE Southbound Base class for specific SNMP MIB implementations.

    \\//
     \/apor IO
"""

import logging

logger = logging.getLogger(__name__)


class SnmpMib(object):
    """Base class for SNMP MIB implementations.
    SnmpMib is a collection of SnmpTable."""

    def __init__(self):
        """Subclasses should define their SnmpTables here in a list. Calling
        the constructor loads the table data automatically."""
        self.name = None
        self.tables = None

    def dump(self):
        """Dump all tables to the log as CSV."""
        logger.debug('Dumping SnmpMib {}.'.format(self.name if self.name else ''))
        for table in self.tables:
            table.dump()
        logger.debug('End SnmpMib dump {}.'.format(self.name if self.name else ''))

    def load(self):
        """Load data for all tables defined in self.tables."""
        for table in self.tables:
            table.load()

    def unload(self):
        """Unload data for all tables defined in self.tables."""
        for table in self.tables:
            table.unload()
