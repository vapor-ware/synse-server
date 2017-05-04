#!/usr/bin/env python
""" Base class for all IPMI auth classes.

    Author: Erick Daniszewski
    Date:   09/02/2016
    
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
import abc


class IPMIAuthType(object):
    """ Base class for the auth-based message wrappers.

    This is primarily initialized within an IPMI object to frame up the
    message data appropriately, based on the authentication type of the
    packet.
    """
    __metaclass__ = abc.ABCMeta

    auth_type = None

    def __init__(self, ipmi_packet):
        self._header = []
        self._body = []

        # define all fields which are supported in IPMI commands. since all auth
        # types inherit from this, the fields here should reflect all possibilities
        # across all auth types.
        # -- header --
        self.authentication_type = None
        self.payload_type = None
        self.session_sequence_number = None
        self.session_id = None
        self.authentication_code = None
        self.payload_length = None

        # -- body --
        self.target_address = None
        self.target_lun = None
        self.header_checksum = None
        self.source_address = None
        self.source_lun = None
        self.command = None
        self.signature = None
        self.completion_code = None
        self.data = None
        self.data_checksum = None
        self.message_tag = None
        self.privilege_level = None

        self.authentication_payload = None
        self.authentication_payload_type = None
        self.authentication_payload_len = None
        self.authentication_algorithm = None
        self.integrity_payload = None
        self.integrity_payload_type = None
        self.integrity_payload_len = None
        self.integrity_algorithm = None
        self.confidentiality_payload = None
        self.confidentiality_payload_type = None
        self.confidentiality_payload_len = None
        self.confidentiality_algorithm = None
        self.confidentiality_trailer = None

        self.remote_session_id = None
        self.bmc_session_id = None
        self.console_random = None
        self.bmc_random = None
        self.system_guid = None
        self.username_length = None
        self.username = None
        self.key_exchange_auth_code = None
        self.integrity_check_value = None
        self.sik = None
        self.k1 = None
        self.k2 = None

        self.iv = None
        self.pad = None

        # flag for presence/absence of integrity authentication
        self.is_authenticated = False

        # flag for presence/absence of payload encryption
        self.is_encrypted = False

        # the ipmi packet which contains the auth type instance. this is
        # the parent and is required here so that this class can get and set
        # the data values needed by the ipmi protocol object for further
        # processing by the mock bmc.
        self.ipmi_packet = ipmi_packet

        # for convenience, include a reference to the bmc object
        self.bmc = self.ipmi_packet.bmc if ipmi_packet else None

        # flag to indicate that the packet is the first for the session so that
        # the subsequent request can appropriately get the new bmc_session_id
        self.is_new_session = False

        # a temporary home for the session context when the session is closed.
        # the action on closing the session is to remove the session and its context
        # from those active tracked sessions. when this happens and the close
        # session response is built, it looks for the session context which is
        # no longer there. this variable is used to persist the context within the
        # request state (as opposed to session state) so that the response can be
        # properly built.
        self.session_close_ctx = None

        # parse the ipmi packet
        self.parse()

    def to_bytes(self):
        """ Convenience method to get the packet as a list of bytes.

        If either the internal members for the header and body are not filled
        out, this will raise an exception as one cannot serialize to bytes
        if the byte data is missing.

        Returns:
            list[int]: a list of ordinal byte values which make up the packet
        """
        if not self._header or not self._body:
            raise ValueError('Missing values for IPMI header or body - unable to write to bytes.')
        return self._header + self._body

    @abc.abstractmethod
    def parse(self):
        """ Parse the raw data of the parent IPMI packet into the appropriate fields for the
        given type of the incoming payload.

        The parsing of the raw data is largely based on the authentication/payload type. Each
        subclass of this class will represent one of the supported authentication types since
        the different authentication types tend to have slight variances in packet structure.

        Within each subclass, it is up to this `parse` method in order to further differentiate
        the payload type, e.g. is it encrypted / integrity authenticated?

        The end result of this parse process will transfer the bytes from their raw format to
        their corresponding named field of this object, making access easier. Additionally,
        each subclass should define an `update_ctx` method which will update the context object
        stored in the mock BMC with any relevant values from this packet. The `update_ctx` method
        can either be called using a `super()` call, by manually invoking `update_ctx`, or not
        at all if there is no context to be updated.
        """
        self.update_ctx()

    @abc.abstractmethod
    def update_ctx(self):
        """ Update the Mock BMC context object.

        This method should be overridden for all subclasses to define which data gets put into
        the session context, if any.
        """
        raise NotImplemented

    @abc.abstractmethod
    def build_response(self, request, response_data, raw_data):
        """ Build the current IPMI packet into a response for the given IPMI request
        packet.

        Note that this should really only be called on a newly initialized packet
        data object, or else the state will be overwritten.

        Args:
            request (IPMI): the IPMI object representing the request to build a
                response for.
            response_data (list[int]): the bytes which make up the response's
                data field.
            raw_data (bool): flag to indicate whether or not the response data
                should be used as the raw packet response or whether it should
                be framed.
        """
        raise NotImplemented

    @abc.abstractmethod
    def set_header_from_state(self):
        """ Update the object's header value based on the individual values currently
        defined in its instance state.
        """
        raise NotImplemented

    @abc.abstractmethod
    def set_body_from_state(self):
        """ Update the object's body value based on the individual values currently
        defined in its instance state.
        """
        raise NotImplemented

    @property
    def header(self):
        return self._header

    @property
    def body(self):
        return self._body
