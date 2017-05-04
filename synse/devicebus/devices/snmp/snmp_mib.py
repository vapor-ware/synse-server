#!/usr/bin/env python
""" Synse Base class for specific SNMP MIB implementations.

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

logger = logging.getLogger(__name__)


class SnmpMib(object):
    """ Base class for SNMP MIB implementations.

    SnmpMib is a collection of SnmpTable.
    """

    def __init__(self):
        """ Subclasses should define their SnmpTables here in a list.

        Calling the constructor loads the table data automatically.
        """
        self.name = None
        self.tables = None

    def dump(self):
        """ Dump all tables to the log as CSV.
        """
        logger.debug('Dumping SnmpMib {}.'.format(self.name if self.name else ''))
        for table in self.tables:
            table.dump()
        logger.debug('End SnmpMib dump {}.'.format(self.name if self.name else ''))

    def load(self):
        """ Load data for all tables defined in self.tables.
        """
        for table in self.tables:
            table.load()

    def unload(self):
        """ Unload data for all tables defined in self.tables.
        """
        for table in self.tables:
            table.unload()
