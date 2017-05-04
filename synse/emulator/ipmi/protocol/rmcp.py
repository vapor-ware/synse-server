#!/usr/bin/env python
""" RMCP protocol model for ease of use in emulator.

    Author: Erick Daniszewski
    Date:   08/29/2016
    
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
from protocol_base import ProtocolBase
from ipmi import IPMI
from asf import ASF


class RMCP(ProtocolBase):
    """ Object representing an incoming RMCP packet.

    The packet formats for this model were taken from:
    http://www.dmtf.org/sites/default/files/standards/documents/DSP0136.pdf
    and is also described in the IPMI 2.0 spec document
    """
    asf_header  = [0x06, 0x00, 0xff, 0x06]
    ipmi_header = [0x06, 0x00, 0xff, 0x07]

    def __init__(self, raw_data, bmc):
        """ Initialize an instance of the RMCP object.

        Args:
            raw_data (list | str): the raw packet data
            bmc (MockBMC): the Mock BMC used for the emulator.

        Returns:
            RMCP
        """
        self.bmc = bmc
        self.user = bmc.username
        self.password = bmc.password

        if not isinstance(raw_data, list):
            raw_data = list(raw_data)
        self.raw_data = raw_data

        if len(self.raw_data) < 4:
            raise ValueError('Fewer than 4 bytes found - cannot determine header, invalid packet.')

        # get the rmcp header and body and validate the header bytes
        self._header = self.raw_data[:4]
        self._body = self.raw_data[4:]
        super(RMCP, self).__init__()

        # determine the message type of the rmcp body and instantiate a
        # proper wrapper object for that message class
        self.message = self._resolve_message_class()

    def _resolve_message_class(self):
        """ Use the message data to determine the message class and generate
        the appropriate wrapper class based on that message class.

        as per the rmcp spec, the class of message is one byte at 03h offset where:
          Bit(s)    Description
         --------  -------------
            7       Message type. Set to 1 to indicate an Acknowledge message.
                    Set to 0 otherwise.
           6:4      Reserved. Set to 000b.
           3:0      Message class. Set to one of the following values:
                      0-5     Reserved
                      6       ASF
                      7       IPMI
                      8       OEM
                      9-15    Reserved

        Returns:
            ASF | IPMI: a wrapper class for the specified RMCP message format.
        """
        _msg_class = ord(self.header[3])

        if (_msg_class >> 7) & 1:
            _msg_class ^= 1 << 7

        # asf
        if _msg_class == 6:
            return ASF(self, self._body)

        # ipmi
        elif _msg_class == 7:
            return IPMI(self, self._body)

        else:
            raise ValueError('Currently only support ASF and IPMI message classes.')

    def validate(self):
        # validate the RMCP header
        _version, _reserved, _seq_num, _msg_class = self.header

        # check that the packet version matches with ASF RMCP v1.0
        if _version != chr(0x06):
            raise ValueError('Expected ASF RMCP version 1.0 - unexpected version byte: {}'.format(hex(ord(_version))))

        if _reserved != chr(0x00):
            raise ValueError('Malformed packet - reserved header byte not 0x00')

    def is_asf(self):
        return self.message and isinstance(self.message, ASF)

    def is_ipmi(self):
        return self.message and isinstance(self.message, IPMI)

    @property
    def body(self):
        return self._body

    @property
    def header(self):
        return self._header
