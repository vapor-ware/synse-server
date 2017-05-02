#!/usr/bin/env python
""" Auth type NONE

    Author: Erick Daniszewski
    Date:   09/02/2016
    
    \\//
     \/apor IO
"""
import auth_base
import auth_types


class AuthNone(auth_base.IPMIAuthType):
    """ Packet data wrapper for messages with No Authentication.
    """
    auth_type = auth_types.NONE

    def __init__(self, ipmi_packet):
        super(AuthNone, self).__init__(ipmi_packet)

    def update_ctx(self):
        # no context needs to be updated here, so consider this a no-op
        pass

    def parse(self):
        data = self.ipmi_packet.raw_data

        # if the ipmi packet's raw data is specified as None, we use that internally
        # to indicate that an IPMI packet is being built by hand, not parsed from a
        # byte list. this is the case for generating response packets. in this case,
        # just return without updating any state.
        if data is None:
            return

        # parse the header
        self._header = map(ord, data[:10])

        self.authentication_type = self._header[0]
        self.session_sequence_number = self._header[1:5]
        self.session_id = self._header[5:9]
        self.payload_length = self._header[9]

        # parse the body
        self._body = map(ord, data[10:])

        if len(self._body) != self.payload_length:
            raise ValueError('Payload length does not match the specified length in header.')

        self.target_address = self._body[0]
        self.target_lun = self._body[1]
        self.header_checksum = self._body[2]
        self.source_address = self._body[3]
        self.source_lun = self._body[4]
        self.command = self._body[5]

        # the last byte is the checksum, so we will not include that, but will consume
        # everything else up to that final byte
        self.data = self._body[6:self.payload_length - 1]
        self.data_checksum = self._body[self.payload_length - 1]

    def set_header_from_state(self):
        # Note: order is important here, since it determines the oder in which the bytes
        # get packed into the header byte list.
        header_list = [
            self.authentication_type,
            self.session_sequence_number,
            self.session_id,
            self.payload_length
        ]

        header = []
        for item in header_list:
            if item is None:
                continue

            if isinstance(item, list):
                header.extend(item)
            else:
                header.append(item)

        self._header = header

    def set_body_from_state(self):
        # Note: order is important here, since it determines the oder in which the bytes
        # get packed into the header byte list.
        body_list = [
            self.target_address,
            self.target_lun,
            self.header_checksum,
            self.source_address,
            self.source_lun,
            self.command,
            self.completion_code,
            self.data,
            self.data_checksum
        ]

        body = []
        for item in body_list:
            if item is None:
                continue

            if isinstance(item, list):
                body.extend(item)
            else:
                body.append(item)

        self._body = body

    def build_response(self, request, response_data, raw_data):
        # -------------------
        # -- RESPONSE BODY --
        # -------------------

        if raw_data:
            self.data = response_data if response_data is not None else []

        else:
            # flip the target and source addresses
            self.target_address = request.source_address
            self.source_address = request.target_address

            # target lun/netfn should indicate response
            self.target_lun = ((request.target_lun >> 2) + 1) << 2

            # compute the checksum
            self.header_checksum = 0x100 - ((self.target_address + self.target_lun) % 256)

            # source lun appears to stay the same via wireshark
            self.source_lun = request.source_lun

            # keep the same command
            self.command = request.command

            # set the completion code as success (0x00) if we did not specify an
            # error completion code in the request packet from earlier processing.
            self.completion_code = 0x00 if request.completion_code is None else request.completion_code

            # get the data
            self.data = response_data if response_data is not None else []

            # calculate the data checksum
            chk = 0

            _data = self.data if self.data is not None else []
            for byte in [self.source_address, self.source_lun, self.command] + _data:
                chk = (chk + byte) % 256
            chk = 0x100 - chk
            self.data_checksum = chk

        # build the list of bytes in the packet body - this will be used during response
        # header creation to generate the auth code and data length values
        self.set_body_from_state()

        # ----------------------
        # -- RESPONSE HEADER ---
        # ----------------------

        # use the same auth type in the response
        self.authentication_type = request.authentication_type

        # increment the session sequence number on the response, unless the current
        # sequence number is 0x00000000, since that tends to be the placeholder value
        seq = request.session_sequence_number
        if seq.count(0x00) != 4:
            seq = [seq[0] + 1] + seq[1:]
        self.session_sequence_number = seq

        # use the same session id in the response
        self.session_id = request.session_id

        # set the length of the ipmi payload
        self.payload_length = len(self.body)

        self.set_header_from_state()
