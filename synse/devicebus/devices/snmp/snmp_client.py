""" Synse SNMP Client.

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

from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.proto.rfc1905 import NoSuchInstance

logger = logging.getLogger(__name__)


class SnmpClient(object):
    """ SNMP client is a thin wrapper around pysnmp.

    Everything here is generic SNMP. No translation layer to Synse belongs here.
    """

    def __init__(self, **kwargs):
        """ Constructor. All kwargs are required.
        """

        # Name or IP of the SNMP server.
        self.snmp_server = kwargs['snmp_server']
        # Port for the SNMP server.
        self.snmp_port = int(kwargs['snmp_port'])
        # SNMP community string for reads.
        self.community_string_read = kwargs['community_string_read']
        # SNMP community string for writes. (Will also work for reads.)
        self.community_string_write = kwargs['community_string_write']
        # SNMP protocol version.
        self.snmp_version = kwargs['snmp_version']
        # For now support SNMP v2c.
        if self.snmp_version != 'v2c':
            raise ValueError('Only SNMP v2c is supported at this time.')

    def get(self, oid):
        """ Snmp wrapper taking a string oid.

        Args:
            oid (str): a string oid such as 1.3.6.1.4.1.61439.6.5.1.2.1.10.3.

        Returns:
            the single row result.
        """
        cmd_generator = cmdgen.CommandGenerator()

        error_indication, error_status, error_index, var_binds = cmd_generator.getCmd(
            cmdgen.CommunityData(self.community_string_read),
            cmdgen.UdpTransportTarget((self.snmp_server, self.snmp_port)),
            oid)

        self._check_for_errors(error_indication, error_status, error_index, var_binds)
        if len(var_binds) != 1:
            raise ValueError('More than one result on a get: {}'.format(var_binds))

        # Return None rather than a NoSuchInstanceObject if nothing is at the OID.
        if var_binds[0][1].__class__ is NoSuchInstance:
            return None
        return var_binds

    def set(self, data):
        """ SNMP set wrapper taking a community string and a string oid such
        as '1.3.6.1.4.1.61439.6.5.1.2.1.10.3'

        Args:
            data (tuple): a tuple of OID and the data to set at the OID.

        Returns:
            the updated data on success.

        Raises:
            ValueError: there is no OID to set or caller does not have write
                credentials.
        """
        logger.debug('SnmpClient set {}'.format(data))
        cmd_generator = cmdgen.CommandGenerator()

        error_indication, error_status, error_index, var_binds = cmd_generator.setCmd(
            cmdgen.CommunityData(self.community_string_write),
            cmdgen.UdpTransportTarget((self.snmp_server, self.snmp_port)),
            data
        )

        self._check_for_errors(error_indication, error_status, error_index, var_binds)

        # Need to error out when there is no OID to set.
        # The SNMP protocol 'succeeds' and gives no NoSuchInstance.
        if var_binds[0][1].__class__ is NoSuchInstance:
            logger.debug('set var_binds {}'.format(var_binds))
            # This can happen in the emulator when the writecache is not
            # properly setup on the OID.
            raise ValueError('No oid to set at {}'.format(var_binds[0][0]))

        if len(var_binds) != 1:
            raise ValueError('More than one result on a set: {}'.format(var_binds))

        return var_binds[0]

    def walk(self, oid):
        """ Snmp walk wrapper taking a string oid such as '1.3.6.1'

        Args:
            oid (str): a string OID (Object Identifier).

        Returns:
            list: he SNMP result set.

        Raises:
            ValueError: on any failure.
        """
        logger.debug('SnmpClient walk {}'.format(oid))
        cmd_generator = cmdgen.CommandGenerator()

        error_indication, error_status, error_index, var_binds = cmd_generator.nextCmd(
            cmdgen.CommunityData(self.community_string_read),
            cmdgen.UdpTransportTarget((self.snmp_server, self.snmp_port)),
            oid)

        self._check_for_errors(error_indication, error_status, error_index, var_binds)
        return SnmpClient._filter_walk_results(var_binds, oid)

    # region private

    @staticmethod
    def _check_for_errors(error_indication, error_status, error_index, var_binds):
        """ Checks for errors from any of the SNMP commands. Fails the test
        if any errors.

        Args:
            error_indication (str): True value indicates SNMP engine error.
            error_status (str): True value indicates SNMP PDU error.
            error_index (int): non-zero value refers to varBinds[errorIndex-1]
            var_binds (tuple): a sequence of ObjectType class instances representing
                MIB variables returned in SNMP response.
        """
        if error_indication:
            msg = 'Error Indication: {}'.format(error_indication)
            logger.error(msg)
            raise ValueError(msg)
        elif error_status:
            msg = 'Error Status: {} at {}'.format(
                error_status.prettyPrint(), error_index and var_binds[int(error_index) - 1][0] or '?')
            logger.error(msg)
            raise ValueError(msg)

    @staticmethod
    def _filter_walk_results(var_binds, walk_oid):
        """ This is a workaround for a ticket where walk can return extra rows.

        Filter them out here for now. This code should not need to be here,
        it's a safety for a previous issue.

        Args:
            var_binds (list): walk results to filter.
            walk_oid (str): the OID of the row we are filtering.

        Returns:
            list: filtered list of walk results.
        """
        logger.debug('Filtering walk results. walk_oid {} count {}'.format(walk_oid, len(var_binds)))
        filtered_results = []
        excluded = []
        for row in var_binds:
            oid = str(row[0][0].getOid())
            if oid.startswith(walk_oid):
                filtered_results.append(row)
            else:
                excluded.append(row)

        if len(excluded) > 0:
            logger.error(
                'Excluded {} rows from walk results. Returning {}.'.format(
                    len(excluded), len(filtered_results)))
            logger.error('Excluded:')
            for row in excluded:
                logger.error(row)
            logger.error('Returning:')
            for row in filtered_results:
                logger.error(row)

        return filtered_results

    # endregion
