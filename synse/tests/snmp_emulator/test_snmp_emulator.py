#!/usr/bin/env python
""" Synse SNMP Emulator Tests

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
import unittest
from subprocess import PIPE, Popen

from pysnmp.entity.rfc3413.oneliner import cmdgen
from pysnmp.hlapi import CommunityData
from pysnmp.hlapi import ContextData
from pysnmp.hlapi import getCmd
from pysnmp.hlapi import ObjectIdentity
from pysnmp.hlapi import ObjectType
from pysnmp.hlapi import SnmpEngine
from pysnmp.hlapi import UdpTransportTarget

from pysnmp.proto.rfc1902 import Integer
from pysnmp.proto.rfc1902 import Integer32
from pysnmp.proto.rfc1905 import NoSuchInstance
from pysnmp.proto.rfc1902 import ObjectIdentifier
from pysnmp.proto.rfc1902 import ObjectName
from pysnmp.proto.rfc1902 import OctetString
from pysnmp.proto.rfc1902 import TimeTicks

logger = logging.getLogger(__name__)


COMMUNITY_STRING_READ_ONLY = 'emulator-test/public'
COMMUNITY_STRING_READ_WRITE = 'emulator-test/private'
SNMP_SERVER = 'snmp-emulator'
SNMP_PORT = 11012


class SnmpEmulatorTestCase(unittest.TestCase):
    """
    Testing for the SNMP emulator.
    """

    # region private

    def _check_for_errors(self, error_indication, error_status, error_index, var_binds):
        """
        Checks for errors from any of the SNMP commands. Fails the test if any errors.
        :param error_indication: True value indicates SNMP engine error.
        :param error_status: True value indicates SNMP PDU error.
        :param error_index: Non-zero value refers to varBinds[errorIndex-1]
        :param var_binds: A sequence of ObjectType class instances representing
        MIB variables returned in SNMP response.
        :return: Nothing.
        """
        if error_indication:
            msg = 'Error Indication: {}'.format(error_indication)
            logger.error(msg)
            self.fail(msg)
        elif error_status:
            msg = 'Error Status: {} at {}'.format(
                error_status.prettyPrint(), error_index and var_binds[int(error_index) - 1][0] or '?')
            logger.error(msg)
            self.fail(msg)

    # endregion

    # region Wrappers

    def snmp_get(self, community_string, oid):
        """
        Snmp wrapper taking a string oid.
        :param community_string: The SNMP community string to use. Here public is read-only and private is
        read/write.
        :param oid: A string oid such as 1.3.6.1.4.1.61439.6.5.1.2.1.10.3.
        :return: The single row result.
        """
        cmd_generator = cmdgen.CommandGenerator()

        error_indication, error_status, error_index, var_binds = cmd_generator.getCmd(
                    cmdgen.CommunityData(community_string),
                    cmdgen.UdpTransportTarget((SNMP_SERVER, SNMP_PORT)),
                    oid,
                    lexicographicMode=True,
                    ignoreNonIncreasingOid=True)

        self._check_for_errors(error_indication, error_status, error_index, var_binds)
        self.assertEquals(1, len(var_binds))
        logger.debug('get result: {}'.format(var_binds[0]))

        # Return None rather than some funky NoSuchInstanceObject if nothing is at the OID.
        if var_binds[0][1].__class__ is NoSuchInstance:
            return None
        return var_binds[0]

    def snmp_get_descriptive(self, community_string, descriptive_oid):
        """
        Snmp get wrapper taking a descriptive oid.
        :param community_string: The SNMP community string to use. Here public is read-only and private is
        read/write.
        :param descriptive_oid: Descriptive oid per pysnmp.
        :return: The single row result.
        """
        error_indication, error_status, error_index, var_binds = next(
            getCmd(SnmpEngine(),
                   CommunityData(community_string, mpModel=0),
                   UdpTransportTarget((SNMP_SERVER, SNMP_PORT)),
                   ContextData(),
                   descriptive_oid))

        self._check_for_errors(error_indication, error_status, error_index, var_binds)
        self.assertEquals(1, len(var_binds))
        logger.debug('get result: {}'.format(var_binds[0]))

        # Return None rather than some funky NoSuchInstanceObject if nothing is at the OID.
        if var_binds[0][1].__class__ is NoSuchInstance:
            return None
        return var_binds[0]

    def snmp_set(self, community_string, data):
        """
        SNMP set wrapper taking a community string and a string oid such as '1.3.6.1.4.1.61439.6.5.1.2.1.10.3'
        :param community_string: The SNMP community string to use. Here public is read-only and private is
        read/write.
        :param data: A tuple of OID and the data to set at the OID.
        :return: The updated data on success.
        :raises: ValueError when there is no OID to set or caller does not have write credentials.
        """
        cmd_generator = cmdgen.CommandGenerator()
        logger.debug('snmp_set:')
        logger.debug('data: {}'.format(data))

        error_indication, error_status, error_index, var_binds = cmd_generator.setCmd(
            cmdgen.CommunityData(community_string),
            cmdgen.UdpTransportTarget((SNMP_SERVER, SNMP_PORT)),
            data
        )

        self._check_for_errors(error_indication, error_status, error_index, var_binds)

        logger.debug('printing set result')
        for name, val in var_binds:
            logger.debug('{} = {}'.format(name.prettyPrint(), val.prettyPrint()))
        logger.debug('end printing set result')

        logger.debug('result:       {}'.format(var_binds[0][1]))
        logger.debug('result class: {}'.format(var_binds[0][1].__class__))
        logger.debug('result type:  {}'.format(type(var_binds[0][1])))

        # Need to error out when there is no OID to set. Unclear why pysmp 'succeeds' and gives no error.
        if var_binds[0][1].__class__ is NoSuchInstance:
            raise ValueError('No oid to set at {}'.format(var_binds[0][0]))

        self.assertEquals(1, len(var_binds))  # Returns the written data.
        return var_binds[0]

    def snmp_walk(self, oid):
        """
        Snmp walk wrapper taking a string oid such as '1.3.6.1'
        :param oid: A string OID (Object Identifier).
        :return: The SNMP result set.
        """
        cmd_generator = cmdgen.CommandGenerator()
        error_indication, error_status, error_index, var_binds = cmd_generator.nextCmd(
                    cmdgen.CommunityData(COMMUNITY_STRING_READ_ONLY),
                    cmdgen.UdpTransportTarget((SNMP_SERVER, SNMP_PORT)),
                    oid,
                    lexicographicMode=True,
                    ignoreNonIncreasingOid=True)

        self._check_for_errors(error_indication, error_status, error_index, var_binds)

        logger.debug('walk result:')
        for row in var_binds:
            logger.debug(row)

        return var_binds

    # endregion

    # region Tests

    def test_sanity(self):
        """
        Simple SNMP walk command line. Verify we get output and no unreasonable stderr. Happy case.
        """
        logger.debug('Start Test: test_sanity')
        proc = Popen(['snmpwalk', '-v2c', '-c', 'public', ':'.join([SNMP_SERVER, str(SNMP_PORT)]), '.1.3.6.1'],
                     stdin=PIPE, stdout=PIPE, stderr=PIPE)
        out, error = proc.communicate()
        out_lines = out.splitlines()
        error_lines = error.splitlines()
        self.assertEquals(399, len(out_lines))  # This different than pysnmp due to newlines.
        self.assertEquals(1, len(error_lines))
        logger.debug('snmpwalk output start')
        logger.debug(out)
        logger.debug('snmpwalk output end')
        # Not clear why we get this in the output, but don't worry about it.
        self.assertEquals('Created directory: /var/lib/snmp/mib_indexes\n', error)

    def test_get_descriptive(self):
        """
        Test simple SNMP get. Happy case. We have tests for string OIDs in the set cases.
        """
        logger.debug('Start Test: test_get')
        result = self.snmp_get_descriptive(
            COMMUNITY_STRING_READ_ONLY, ObjectType(ObjectIdentity('SNMPv2-MIB', 'sysDescr', 0)))

        logger.debug('descriptive get result: {}'.format(result))

        # Validate response.
        self.assertEquals(ObjectType, result.__class__)
        self.assertEquals('1.3.6.1.2.1.1.1.0', str((result[0]).getOid()))
        self.assertEquals('TEST-SYSTEM-DESCRIPTION', result[1])

    def test_walk(self):
        """
        Test walk of each MIB we are emulating with the pysnmp client. Happy case.
        """
        logger.debug('Start Test: test_walk')
        var_binds = self.snmp_walk('1.3.6.1')
        self.assertEquals(398, len(var_binds))

        # Collect all types here so that we can test sets against them.
        snmp_types = set()
        for row in var_binds:
            class_string = str((row[0][1]).__class__)
            if class_string not in snmp_types:
                logger.debug('adding class_string {}'.format(class_string))
                snmp_types.add(class_string)

        logger.debug('Dumping all walked types.')  # So that we can write set tests for them.
        logger.debug(snmp_types)

        # NOTE: Not clear that we can set the __builtin__ types. Not clear that we can create them.
        # Also - TimeStamp and TimeTicks are different.
        expected_snmp_types = {
            # ObjectIdentity is a wrapper around ObjectIdentifier and ObjectName.
            """<class 'pysnmp.smi.rfc1902.ObjectIdentity'>""",
            """<class 'pysnmp.proto.rfc1902.Integer32'>""",
            """<class 'DisplayString'>""",
            """<class 'TimeStamp'>""",
            """<class 'pysnmp.proto.rfc1902.Integer'>""",
            """<class 'pysnmp.proto.rfc1902.OctetString'>""",
            """<class 'pysnmp.proto.rfc1902.TimeTicks'>"""
        }

        self.assertTrue(snmp_types == expected_snmp_types,
                        'Unrecognized SNMP type in walk. Please add a get/set test for it.'
                        ' Expected: {}'
                        ' Actual:   {}'.format(expected_snmp_types, snmp_types))

    def test_get_set_string(self):
        """Test get and set on a writable string OID. Happy case."""
        logger.debug('Start Test: test_get_set_string')

        test_oid = '1.3.6.1.4.1.61439.6.5.1.2.1.10.25'
        result = self.snmp_get(COMMUNITY_STRING_READ_WRITE, test_oid)

        initial_value = result[1]
        self.assertEqual(test_oid, str(result[0]))
        self.assertEqual('ce vieux', str(initial_value),
                         'Failure here is a test reentrancy issue.')

        # Set to something different.
        logger.debug('set:')
        new_value = OctetString('Something different!')
        set_param = (ObjectName(test_oid), new_value)
        result = self.snmp_set(COMMUNITY_STRING_READ_WRITE, set_param)
        logger.debug('set result: '.format(result))

        self.assertEqual(new_value, result[1], 'Validating set.')

        # Set back to original and fail with a message about reentrancy if we can't.
        set_param = (ObjectName(test_oid), initial_value)
        result = self.snmp_set(COMMUNITY_STRING_READ_WRITE, set_param)
        logger.debug('second set result: {}'.format(result[1]))

        self.assertEqual(initial_value, result[1],
                         'Validating second set. A failure here may affect subsequent tests.')

    def test_get_set_oid(self):
        """Test get and set on a writable OID with OID data. Happy case."""
        logger.debug('Start Test: test_get_set_oid')

        test_oid = '1.3.6.1.2.1.1.9.1.2.8'
        result = self.snmp_get(COMMUNITY_STRING_READ_WRITE, test_oid)

        initial_value = result[1]
        self.assertEqual(test_oid, str(result[0]))
        self.assertEqual('1.3.6.1.3.163.152.52.135', str(initial_value),
                         'Failure here is a test reentrancy issue.')

        # Set to something different.
        logger.debug('test_get_set_oid set:')
        new_value = ObjectIdentifier('1.3.6.1.3.163.152.52.100')
        set_param = (ObjectName(test_oid), new_value)
        result = self.snmp_set(COMMUNITY_STRING_READ_WRITE, set_param)
        logger.debug('set result: '.format(result))

        self.assertEqual(new_value, result[1], 'Validating set.')

        # Set back to original and fail with a message about reentrancy if we can't.
        set_param = (ObjectName(test_oid), initial_value)
        result = self.snmp_set(COMMUNITY_STRING_READ_WRITE, set_param)
        logger.debug('second set result: {}'.format(result[1]))

        self.assertEqual(initial_value, result[1],
                         'Validating second set. A failure here may affect subsequent tests.')

    def test_get_set_time_ticks(self):
        """Test get and set on a writable OID with TimeTicks data. Happy case."""
        logger.debug('Start Test: test_get_set_time_ticks')

        test_oid = '1.3.6.1.2.1.1.3.0'
        result = self.snmp_get(COMMUNITY_STRING_READ_WRITE, test_oid)

        initial_value = result[1]
        self.assertEqual(test_oid, str(result[0]))
        self.assertEqual('3094296065', str(initial_value),
                         'Failure here is a test reentrancy issue.')

        # Set to something different.
        logger.debug('set:')
        new_value = TimeTicks(3094296060)
        set_param = (ObjectName(test_oid), new_value)
        result = self.snmp_set(COMMUNITY_STRING_READ_WRITE, set_param)
        logger.debug('set result: '.format(result))

        self.assertEqual(new_value, result[1], 'Validating set.')

        # Set back to original and fail with a message about reentrancy if we can't.
        set_param = (ObjectName(test_oid), initial_value)
        result = self.snmp_set(COMMUNITY_STRING_READ_WRITE, set_param)
        logger.debug('second set result: {}'.format(result[1]))

        self.assertEqual(initial_value, result[1],
                         'Validating second set. A failure here may affect subsequent tests.')

    def test_get_set_integer(self):
        """Test get and set on a writable OID with Integer data. Happy case."""
        logger.debug('Start Test: test_get_set_integer')

        test_oid = '1.3.6.1.4.1.61439.6.5.1.2.1.11.8'
        result = self.snmp_get(COMMUNITY_STRING_READ_WRITE, test_oid)

        initial_value = result[1]
        self.assertEqual(test_oid, str(result[0]))
        self.assertEqual('17', str(initial_value),
                         'Failure here is a test reentrancy issue.')

        # Set to something different.
        logger.debug('set:')
        new_value = Integer(18)
        set_param = (ObjectName(test_oid), new_value)
        result = self.snmp_set(COMMUNITY_STRING_READ_WRITE, set_param)
        logger.debug('set result: '.format(result))

        self.assertEqual(new_value, result[1], 'Validating set.')

        # Set back to original and fail with a message about reentrancy if we can't.
        set_param = (ObjectName(test_oid), initial_value)
        result = self.snmp_set(COMMUNITY_STRING_READ_WRITE, set_param)
        logger.debug('second set result: {}'.format(result[1]))

        self.assertEqual(initial_value, result[1],
                         'Validating second set. A failure here may affect subsequent tests.')

    def test_get_set_integer32(self):
        """Test get and set on a writable OID with Integer32 data. Happy case."""
        logger.debug('Start Test: test_get_set_integer32')
        test_oid = '1.3.6.1.2.1.1.9.1.1.21'
        result = self.snmp_get(COMMUNITY_STRING_READ_WRITE, test_oid)

        initial_value = result[1]
        logger.debug('result[1] {}'.format(result[1]))
        self.assertEqual(test_oid, str(result[0]))
        self.assertEqual('21', str(initial_value),
                         'Failure here is a test reentrancy issue.')

        # Set to something different.
        logger.debug('set:')
        new_value = Integer32(22)
        set_param = (ObjectName(test_oid), new_value)
        result = self.snmp_set(COMMUNITY_STRING_READ_WRITE, set_param)
        logger.debug('set result: '.format(result))

        self.assertEqual(new_value, result[1], 'Validating set.')

        # Set back to original and fail with a message about reentrancy if we can't.
        set_param = (ObjectName(test_oid), initial_value)
        result = self.snmp_set(COMMUNITY_STRING_READ_WRITE, set_param)
        logger.debug('second set result: {}'.format(result[1]))

        self.assertEqual(initial_value, result[1],
                         'Validating second set. A failure here may affect subsequent tests.')

    def test_get_set_read_only(self):
        """Test get and set on an OID that we can read but not write due to read only community string."""
        test_oid = '1.3.6.1.4.1.61439.6.5.1.2.1.10.3'

        result = self.snmp_get(COMMUNITY_STRING_READ_ONLY, test_oid)

        logger.debug('get passed')

        initial_value = result[1]
        self.assertEquals(test_oid, str(result[0]))
        self.assertEquals('whisky au juge blond qui', str(initial_value))

        logger.debug('set:')
        set_param = (ObjectName('1.3.6.1.4.1.61439.6.5.1.2.1.10.3'), OctetString('whisky au juge blond qui'))

        try:
            self.snmp_set(COMMUNITY_STRING_READ_ONLY, set_param)
        except ValueError as ve:
            if 'No oid to set at' in ve.message:
                return  # Pass
            else:
                self.fail('Incorrect error message [{}]'.format(ve.message))
        self.fail('Should have raised ValueError')

    def test_get_set_unknown_oid(self):
        """Test get and set on an OID that the emulator does not know about."""
        logger.debug('Start Test: test_get_set_unknown_oid')

        logger.debug('Start Test: test_get_set_string')

        test_oid = '1.3.6.1.4.1.21111.6.5.1.2.1.10.25'
        result = self.snmp_get(COMMUNITY_STRING_READ_WRITE, test_oid)

        self.assertEqual(None, result, 'Expected None when the OID does not exist.')

        set_param = (ObjectName(test_oid), OctetString('This should fail.'))

        try:
            self.snmp_set(COMMUNITY_STRING_READ_WRITE, set_param)
        except ValueError as ve:
            if 'No oid to set at' in ve.message:
                return  # Pass
            else:
                self.fail('Incorrect error message [{}]'.format(ve.message))
        self.fail('Should have raised ValueError')

    def test_send_incompatible_type(self):
        """Test setting an integer when SNMP expects a string."""
        logger.debug('Start Test: test_send_incompatible_type')

        test_oid = '1.3.6.1.4.1.61439.6.5.1.2.1.10.25'
        result = self.snmp_get(COMMUNITY_STRING_READ_WRITE, test_oid)

        initial_value = result[1]
        self.assertEqual(test_oid, str(result[0]))
        self.assertEqual('ce vieux', str(initial_value),
                         'Failure here is a test reentrancy issue.')

        # Set to an integer when a string is expected.
        # pysnmp gives no such instance again. Still a ValueError.
        logger.debug('set incompatible type:')
        new_value = Integer(3)
        set_param = (ObjectName(test_oid), new_value)

        try:
            self.snmp_set(COMMUNITY_STRING_READ_WRITE, set_param)
        except ValueError as ve:
            if 'No oid to set at' in ve.message:
                return  # Pass
            else:
                self.fail('Incorrect error message [{}]'.format(ve.message))
        self.fail('Should have raised ValueError')

    # TODO: Test traps when we know for sure what we need to do there.

    # endregion
