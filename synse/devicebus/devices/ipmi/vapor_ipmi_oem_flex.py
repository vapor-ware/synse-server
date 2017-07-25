#!/usr/bin/env python
""" Synse IPMI FLEX OEM Extensions

In this case, for Flex servers (Ciii Victoria 2508)

    Author:  andrew
    Date:    9/29/2016

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

from synse.definitions import BMC_PORT
from synse.devicebus.devices.ipmi.vapor_ipmi_common import IpmiCommand
from synse.errors import SynseException


def get_flex_victoria_power_reading(username=None, password=None, ip_address=None,
                                    port=BMC_PORT):
    """ Flex Ciii Victoria 2508 power reading retrieval.

    Uses master r/w command to retrieve the power status from the two PSUs;
    the readings are then summed together and returned. As with many other
    commands, a 'good' power reading is only produced when chassis power is
    'on'. Otherwise, we end up seeing readings that are just 0W. If a PSU
    is missing, we still read both PSUs, and sum what we've got. Even if
    only 1/2 of the PSUs are present, we can still get an accurate reading.

    Args:
        username (str): the username to connect to BMC with.
        password (str): the password to connect to BMC with.
        ip_address (str): the IP Address of the BMC.
        port (int): BMC port.

    Returns:
        dict: power reading information from the remote system.

    Raises:
        SynseException: in cases where BMC is unreachable or an error is
            encountered processing the command.
    """
    psu0_power = 0
    psu1_power = 0

    with IpmiCommand(ip_address=ip_address, username=username, password=password,
                     port=port) as ipmicmd:
        # get PSU0 consumption
        try:
            result = ipmicmd.raw_command(
                netfn=0x06, command=0x52, data=(0xa0, 0xb0, 0x02, 0x96))

            if 'error' in result:
                raise SynseException(
                    'Error executing master r/w command on {} : {}'.format(
                        ip_address, result['error'])
                )
            psu0_power = _convert_linear_11((result['data'][1] << 8) | result['data'][0])
        except Exception:
            # PSU 0 or 1 may be missing, which is fine, so no action needed
            pass

        # get PSU1 consumption
        try:
            result = ipmicmd.raw_command(
                netfn=0x06, command=0x52, data=(0xa0, 0xb2, 0x02, 0x96))

            if 'error' in result:
                raise SynseException(
                    'Error executing master r/w command on {} : {}'.format(
                        ip_address, result['error'])
                )
            psu1_power = _convert_linear_11((result['data'][1] << 8) | result['data'][0])
        except Exception:
            # PSU 0 or 1 may be missing, which is fine, so no action needed
            pass

    return {'input_power': float(psu0_power + psu1_power)}


def _convert_linear_11(linear_value):
    """ Convert a 16-bit (2-byte) value to float using linear data
    format conversion.

    see http://pmbus.org/Assets/PDFS/Public/PMBus_Specification_Part_II_Rev_1-1_20070205.pdf
    section 7.1 (p21)

    X = Y * 2^N
    ___________________
    |HI BYTE |LO BYTE |
    |--------|--------|
    |76543|21076543210|
    |-----|-----------|
    |  N  |     Y     |
    -------------------

    Args:
        linear_value (int): the incoming linear-encoded value.

    Returns:
        float: the converted value.
    """
    def _twos_comp(val, bits):  # pylint: disable=missing-docstring
        if (val & (1 << (bits - 1))) != 0:
            val = (val - (1 << bits))
        return val

    y = _twos_comp(linear_value & 0b0000011111111111, 11)
    n = _twos_comp(linear_value >> 11, 5)
    return float(y * pow(2, n))
