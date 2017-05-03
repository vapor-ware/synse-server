#!/usr/bin/env python
""" RMCP IPMI message class.

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
import auth


class IPMI(object):
    """ A wrapper around RMCP message data to frame it as an IPMI message.

    This class provides a fairly lightweight wrapper around the message data
    to allow for proper framing as an IPMI packet. It also provides some
    convenience methods for data access and response generation.

    The actual message data lives in the `packet_data` member, which is an
    object determined by the IPMI packet's auth type, however any attributal
    lookup that can be done on that inner object can be done on this object
    because of attribute lookup forwarding, e.g.::

        # initialize an IPMI packet
        >> i = IPMI(wrapper, data)

        # ipmi has no member 'payload_type', but its `packet_data` member does
        >> hasattr(i, 'payload_type')
        False
        >> hasattr(i.packet_data, 'payload_type')
        True

        # a lookup on the IPMI packet will be a lookup on its packet_data member
        >> i.packet_data.payload_type
        0
        >> i.payload_type
        0

    """
    def __init__(self, wrapper, raw_data, auth_type=None):
        self.rmcp_wrapper = wrapper
        self.bmc = wrapper.bmc
        self.raw_data = raw_data

        # when given data via the raw_data parameter, this will go ignored. when no
        # raw_data is given (e.g. None is provided for that parameter), this value
        # will be used to determine what kind of empty IPMI packet to frame up. an
        # exception will be raised if no data is provided and no auth_type is provided
        # since we would have no way to know how to create a valid packet in that case.
        self._auth_type = auth_type

        # holder for the parsed ipmi packet data. this will hold the data parsed
        # from the raw packet data based on the auth type specified in the incoming
        # raw data.
        self.packet_data = None
        self._generate_data_wrapper()

    def __getattr__(self, item):
        try:
            return getattr(self.packet_data, item)
        except:
            return None

    def __setattr__(self, key, value):
        if not hasattr(self, key):
            setattr(self.packet_data, key, value)
        else:
            super(IPMI, self).__setattr__(key, value)

    @property
    def header(self):
        return self.packet_data.header

    @header.setter
    def header(self, data):
        self.packet_data.header = data

    @property
    def body(self):
        return self.packet_data.body

    @body.setter
    def body(self, data):
        self.packet_data.body = data

    def _generate_data_wrapper(self):
        """ Generate the underlying packet data wrapper based on auth type specified
        in packet message.

        Once the type of message is determined, the appropriate auth-based data wrapper
        class is constructed and stored in the `packet_data` member.
        """
        # if there is no raw data, there is nothing to parse - this typically
        # indicates that an IPMI instance is being crafted by hand
        if not self.raw_data:
            if self._auth_type is None:
                raise ValueError('No raw data provided for IPMI packet and no Auth Type specified.')

        # to determine how to parse the incoming raw data, we will need to determine
        # the auth type and parse according to the spec for that auth type.
        else:
            self._auth_type = ord(self.raw_data[0])

        auth_key = self._auth_type

        data_auth_parser_cls = {
            auth.NONE: auth.AuthNone,
            auth.MD5: auth.AuthMD5,
            auth.RMCP: auth.AuthRMCP
        }.get(auth_key, None)

        if data_auth_parser_cls is None:
            raise ValueError('Unexpected or unsupported auth type: {}'.format(hex(self._auth_type)))

        # initializing an IPMIAuthType object will parse the raw data in the correct format
        # compliant to the auth type for that message.
        self.packet_data = data_auth_parser_cls(self)

    def to_bytes(self, stringify=False):
        """ Convenience method to convert the internal packet data to its bytes.

        Args:
            stringify (bool): flag which, when enabled, will return a string representation
                of the bytes, instead of an ordinal list representation.

        Returns:
            list[int]: list of bytes, if stringify=False
            str: byte string, if stringify=True
        """
        packet = self.packet_data.to_bytes()
        if stringify:
            packet = ''.join(map(chr, packet))
        return packet

    def make_response(self, response_data, raw_data=False):
        """ Makes a response for the given request.

        Args:
            response_data (list[int]): the list of bytes which make up the data
                for the response being build
            raw_data (bool): a flag to indicate whether or not to use the specified
                response_data as raw (no packet framing) or not.

        Returns:
            IPMI: an IPMI packet representing the response to this request packet.
        """
        response_pkt = IPMI(wrapper=self.rmcp_wrapper, raw_data=None, auth_type=self.authentication_type)
        response_pkt.packet_data.build_response(self, response_data, raw_data)
        return response_pkt
