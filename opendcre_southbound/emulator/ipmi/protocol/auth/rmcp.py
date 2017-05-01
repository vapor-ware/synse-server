#!/usr/bin/env python
""" Auth type RMCP+

    Author: Erick Daniszewski
    Date:   09/02/2016

    \\//
     \/apor IO
"""
import auth_base
import auth_types
import random
import hashlib
import hmac
from Crypto.Cipher import AES

from auth_context import SessionContext


class AuthRMCP(auth_base.IPMIAuthType):
    """ Packet data wrapper for messages with RMCP+ Authentication.
    """
    auth_type = auth_types.RMCP

    def __init__(self, ipmi_packet):
        super(AuthRMCP, self).__init__(ipmi_packet)

    def update_ctx(self):
        """ Dispatcher to update the BMC session context based on the object's
        payload type.
        """
        # define a no-op method used as the default if no context update method
        # is specified for a given payload type
        def _pass(): pass

        {
            0x10: self._update_for_open_session_request,
            0x12: self._update_for_rakp_1_request
        }.get(self.payload_type, _pass)()

    def _update_for_open_session_request(self):
        """ Update the BMC session context for Open Session Requests.
        """
        # if we get an open session request, there will be no current context
        # because there is no session to associate the context with. as such,
        # we will want to create a session and add the context.
        def get_session_id():
            return [random.randint(1, 255) for _ in range(4)]

        new_session_id = get_session_id()
        while ''.join(map(chr, new_session_id)) in self.bmc._active_sessions:
            new_session_id = get_session_id()

        session_ctx = SessionContext(None)
        session_ctx.privilege_level = 0x04 if self.privilege_level == 0x00 else self.privilege_level
        session_ctx.remote_session_id = self.remote_session_id
        session_ctx.bmc_session_id = new_session_id
        session_ctx.system_guid = self.bmc.system_guid

        # authentication payload
        session_ctx.authentication_payload = self.authentication_payload
        session_ctx.authentication_payload_type = self.authentication_payload_type
        session_ctx.authentication_payload_len = self.authentication_payload_len
        session_ctx.authentication_algorithm = self.authentication_algorithm

        # integrity payload
        session_ctx.integrity_payload = self.integrity_payload
        session_ctx.integrity_payload_type = self.integrity_payload_type
        session_ctx.integrity_payload_len = self.integrity_payload_len
        session_ctx.integrity_algorithm = self.integrity_algorithm

        # confidentiality payload
        session_ctx.confidentiality_payload = self.confidentiality_payload
        session_ctx.confidentiality_payload_type = self.confidentiality_payload_type
        session_ctx.confidentiality_payload_len = self.confidentiality_payload_len
        session_ctx.confidentiality_algorithm = self.confidentiality_algorithm

        # indicate that this request starts a new session
        self.is_new_session = True
        self.bmc_session_id = new_session_id

        # finally, add the context to the newly tracked session
        sess = ''.join(map(chr, new_session_id))
        self.bmc._active_sessions[sess] = {'ctx': session_ctx}

    def _update_for_rakp_1_request(self):
        """ Update the BMC session context for RAKP 1 Requests.
        """
        session = ''.join(map(chr, self.bmc_session_id))

        # first, get the session context. if it does not exist, we have a problem
        if session not in self.bmc._active_sessions:
            raise KeyError('Session ID on incoming request ({}) is not tracked by the BMC.'.format(self.bmc_session_id))

        session_ctx = self.bmc._active_sessions[session]['ctx']

        session_ctx.console_random = self.console_random
        session_ctx.privilege_level = 0x04 if self.privilege_level == 0x00 else self.privilege_level
        session_ctx.username_length = self.username_length
        session_ctx.username = self.username

        # RAKP 1 acts as session activation, so add the session id to the tracked sessions
        self.bmc._active_sessions[session].update({
            'outbound_seq': self.session_sequence_number,
            'privilege': session_ctx.privilege_level
        })

    def parse(self):
        data = self.ipmi_packet.raw_data

        # if the ipmi packet's raw data is specified as None, we use that internally
        # to indicate that an IPMI packet is being built by hand, not parsed from a
        # byte list. this is the case for generating response packets. in this case,
        # just return without updating any state.
        if data is None:
            return

        # ----------------
        # parse the header
        # ----------------
        self._header = map(ord, data[:12])

        self.authentication_type = self._header[0]

        payload = self._header[1]
        self.payload_type = payload & 0b00111111
        self.is_encrypted = bool((payload >> 7) & 0b01)
        self.is_authenticated = bool((payload >> 6) & 0b01)

        self.session_id = self._header[2:6]
        self.session_sequence_number = self._header[6:10]
        self.payload_length = self._header[10:12]

        # make an integer value out of the two bytes which make up payload length
        payload_len = self.payload_length[0]
        payload_len |= self.payload_length[1] << 8

        # with the header parsed, we now want to determine what the body of the packet
        # is and validate it against the length specified in the header.
        #
        # if the packet is authenticated, the remainder of the data includes the auth
        # trailer, so we will want to separate that out prior to comparing the data
        # size.
        remainder = map(ord, data[12:])
        if self.is_authenticated:
            # if authenticated, we should already have a session context defined.
            session_ctx = self.bmc._active_sessions[''.join(map(chr, self.session_id))]['ctx']

            # HMAC-SHA1-96
            if session_ctx.integrity_algorithm == 0x01:
                self.integrity_check_value = remainder[-12:]
                # ipmi spec specifies that the byte preceeding the integrity check should be 0x07
                if remainder[-13] != 0x07:
                    raise ValueError('Integrity validation failed - byte did not match 0x07')
                # get the padding size
                pad_size = remainder[-14]
                # now we can get the body
                body = remainder[:(-14 - pad_size)]

                if len(body) != payload_len:
                    raise ValueError('Payload length does not match header specification')

            else:
                raise ValueError('Unsupported authentication algorithm: {}'.format(self.authentication_type))

        # if the packet is not integrity authenticated, then the remainder of the packet is the
        # body of the packet
        else:
            body = remainder

        # if the payload is encrypted we will want to decrypt it before parsing the bytes of the
        # packet body.
        if self.is_encrypted:

            # if authenticated, we should already have a session context defined.
            session_ctx = self.bmc._active_sessions[''.join(map(chr, self.session_id))]['ctx']

            body = map(ord, data[12:44])
            self.confidentiality_trailer = data[44:]

            iv = body[:16]
            cipher = AES.new(''.join(map(chr, session_ctx.k2[0:16])), AES.MODE_CBC, ''.join(map(chr, iv)))
            decrypted = cipher.decrypt(''.join(map(chr, body[16:])))
            _d = map(ord, decrypted)
            padsize = _d[-1] + 1
            body = _d[:-padsize]

            payload_len = len(body)

        # how the body of the request is parsed will depend on the payload type
        # for the packet, as specified in the header information.

        # ============================
        # open session request (0x10)
        # ============================
        if self.payload_type == 0x10:
            self.bmc.debug('>> Open Session Request')
            self.message_tag = body[0]
            self.privilege_level = body[1]
            self.remote_session_id = body[4:8]

            # *******************************************
            # authentication payload info
            #
            #  byte         desc
            # ------       ---------------------------
            #   1           payload type
            #  2:3          reserved (0x0000)
            #   4           payload length
            #   5           authentication algorithm
            #  6:8          reserved
            # *******************************************
            ap = body[8:16]
            self.authentication_payload = ap
            self.authentication_payload_type = ap[0]
            self.authentication_payload_len = ap[3]
            self.authentication_algorithm = ap[4]

            # *******************************************
            # integrity payload info
            #
            #  byte         desc
            # ------       ---------------------------
            #   1           payload type
            #  2:3          reserved (0x0000)
            #   4           payload length
            #   5           integrity algorithm
            #  6:8          reserved
            # *******************************************
            ip = body[16:24]
            self.integrity_payload = ip
            self.integrity_payload_type = ip[0]
            self.integrity_payload_len = ip[3]
            self.integrity_algorithm = ip[4]

            # *******************************************
            # confidentiality payload info
            #
            #  byte         desc
            # ------       ---------------------------
            #   1           payload type
            #  2:3          reserved (0x0000)
            #   4           payload length
            #   5           confidentiality algorithm
            #  6:8          reserved
            # *******************************************
            cp = body[24:32]
            self.confidentiality_payload = cp
            self.confidentiality_payload_type = cp[0]
            self.confidentiality_payload_len = cp[3]
            self.confidentiality_algorithm = cp[4]

        # ==============================
        # RAKP Message 1 request (0x12)
        # ==============================
        elif self.payload_type == 0x12:
            self.bmc.debug('>> RAKP 1 Request')
            self.message_tag = body[0]

            # bytes 2:4 are reserved

            self.bmc_session_id = body[4:8]
            self.console_random = body[8:24]
            self.privilege_level = body[24]

            # bytes 26:27 are reserved

            self.username_length = body[27]
            self.username = body[28:]

            # here, we want to set the session id of this request to the found
            # bmc session id. this is because the rakp message will have a
            # zeroed out session id, but we need a way to associate the request
            # and response with the correct session context internally.
            self.session_id = self.bmc_session_id

        # ==============================
        # RAKP Message 3 request (0x14)
        # ==============================
        elif self.payload_type == 0x14:
            self.bmc.debug('>> RAKP 3 Request')
            self.message_tag = body[0]
            self.completion_code = body[1]

            # bytes 3:4 reserved

            self.bmc_session_id = body[4:8]
            self.key_exchange_auth_code = body[8:]

            # here, we want to set the session id of this request to the found
            # bmc session id. this is because the rakp message will have a
            # zeroed out session id, but we need a way to associate the request
            # and response with the correct session context internally.
            self.session_id = self.bmc_session_id

        # ==============================
        # IPMI Message (0x00)
        # ==============================
        elif self.payload_type == 0x00:
            self.bmc.debug('>> RMCP+ IPMI Request')
            self.target_address = body[0]
            self.target_lun = body[1]
            self.header_checksum = body[2]
            self.source_address = body[3]
            self.source_lun = body[4]
            self.command = body[5]

            # check the netfn to determine whether or not the incoming request will contain
            # a signature
            netfn = self.target_lun >> 2

            if netfn == 0x2c:
                self.signature = body[6]
                data_idx = 7
            else:
                data_idx = 6

            # the last byte is the checksum, so we will not include that, but consume
            # everything else up to that final byte
            _tmp_data = body[data_idx:payload_len - 1]
            self.data = _tmp_data if _tmp_data else None
            self.data_checksum = body[payload_len - 1]

        # unknown or unsupported
        else:
            raise ValueError('Unknown or unsupported payload type for RMCP message: {}'.format(hex(self.payload_type)))

        # Now that the incoming packet has been parsed and the data collected into the
        # appropriate fields, we want to update the BMC's session context with any relevant
        # values from the packet.
        self.update_ctx()

    def set_header_from_state(self):
        # Note: order is important here, since it determines the oder in which the bytes
        # get packed into the header byte list.
        header_list = [
            self.authentication_type,
            self.payload_type | (self.is_encrypted << 7) | (self.is_authenticated << 6),
            self.session_id,
            self.session_sequence_number,
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
        body_content = {
            0x11: [
                self.message_tag,
                self.completion_code,
                self.privilege_level,
                0x00,  # reserved
                self.remote_session_id,
                self.bmc_session_id,
                self.authentication_payload,
                self.integrity_payload,
                self.confidentiality_payload
            ],
            0x13: [
                self.message_tag,
                self.completion_code,
                [0x00, 0x00],  # reserved
                self.remote_session_id,
                self.bmc_random,
                self.system_guid,
                self.key_exchange_auth_code
            ],
            0x15: [
                self.message_tag,
                self.completion_code,
                [0x00, 0x00],  # reserved
                self.remote_session_id,
                self.integrity_check_value
            ],
            0x00: [
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
        }

        body_list = body_content[self.payload_type]

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

        # get the session context
        if request.is_new_session:
            session_id = request.bmc_session_id
        else:
            session_id = request.session_id

        # if the request was a 'close session' request, the context is stored in
        # the request state. otherwise, get the context from the session state
        if request.session_close_ctx is not None:
            session_ctx = request.session_close_ctx
        else:
            session_ctx = self.bmc._active_sessions[''.join(map(chr, session_id))]['ctx']

        # -------------------
        # -- RESPONSE BODY --
        # -------------------
        if request.payload_type == 0x10:
            # increment the payload type for when the header info is parsed
            self.payload_type = 0x11
            self.bmc.debug('<< Open Session Response')

            self.message_tag = request.message_tag

            # 0x00 = successful completion
            self.completion_code = 0x00

            self.privilege_level = session_ctx.privilege_level

            self.remote_session_id = session_ctx.remote_session_id
            self.bmc_session_id = session_ctx.bmc_session_id

            self.authentication_payload = session_ctx.authentication_payload
            self.integrity_payload = session_ctx.integrity_payload
            self.confidentiality_payload = session_ctx.confidentiality_payload

        elif request.payload_type == 0x12:
            # increment the payload type for when the header info is parsed
            self.payload_type = 0x13
            self.bmc.debug('<< RAKP 2 Response')

            self.message_tag = request.message_tag

            # 0x00 = successful completion
            self.completion_code = 0x00

            self.username_length = session_ctx.username_length
            self.username = session_ctx.username

            self.privilege_level = session_ctx.privilege_level

            self.remote_session_id = session_ctx.remote_session_id
            self.console_random = session_ctx.console_random
            self.bmc_session_id = session_ctx.bmc_session_id
            self.system_guid = session_ctx.system_guid
            self.bmc_random = [random.randint(0, 255) for _ in range(16)]

            # add bmc random to session context
            session_ctx.bmc_random = self.bmc_random

            hmac_data = (
                self.remote_session_id +
                self.bmc_session_id +
                self.console_random +
                self.bmc_random +
                self.system_guid +
                [self.privilege_level] +
                [self.username_length] +
                self.username
            )

            _hmac = hmac.new(
                request.rmcp_wrapper.bmc.password,
                ''.join(map(chr, hmac_data)),
                hashlib.sha1    # FIXME - this should be determined from the integrity type
            )
            self.key_exchange_auth_code = map(ord, _hmac.digest())

            session_ctx.key_exchange_auth_code = self.key_exchange_auth_code

        elif request.payload_type == 0x14:
            # increment the payload type for when the header info is parsed
            self.payload_type = 0x15
            self.bmc.debug('<< RAKP 4 Response')

            self.message_tag = request.message_tag

            self.username_length = session_ctx.username_length
            self.username = session_ctx.username
            self.privilege_level = session_ctx.privilege_level

            # 0x00 = successful completion
            self.completion_code = 0x00
            self.bmc_session_id = session_ctx.bmc_session_id
            self.remote_session_id = session_ctx.remote_session_id

            self.console_random = session_ctx.console_random
            self.bmc_random = session_ctx.bmc_random
            self.system_guid = session_ctx.system_guid

            # generate the integrity check value - this is done such that:
            #  SIK = HMAC_kg (R_m | R_c | Role_m | ULength_m | <UName_m>)
            # which then gets sent back as
            #  SID_m, HMAC_sik (R_m | SID_c | GUID_c)
            #
            # Note: K_[UID] is used in place of Kg if 'one-key' logins are being used.
            # For the emulator, we will only support one key logins for now, so this will
            # always be the case.
            hmac_data = (
                self.console_random +
                self.bmc_random +
                [self.privilege_level] +
                [self.username_length] +
                self.username
            )

            _hmac = hmac.new(
                self.bmc.password,
                ''.join(map(chr, hmac_data)),
                hashlib.sha1
            )
            _sik_digest = _hmac.digest()
            self.sik = map(ord, _sik_digest)
            session_ctx.sik = self.sik

            # now, generate integrity check value
            hmac_data = (
                self.console_random +
                self.bmc_session_id +
                self.system_guid
            )

            _hmac = hmac.new(
                _sik_digest,
                ''.join(map(chr, hmac_data)),
                hashlib.sha1
            )

            self.integrity_check_value = map(ord, _hmac.digest())[:12]
            session_ctx.integrity_check_value = self.integrity_check_value

            # finally, we want to generate additional keying material (see IPMI spec 13.32 -
            # Generating Additional Keying Material)
            session_ctx.k1 = [ord(i) for i in hmac.new(_sik_digest, b'\x01' * 20, hashlib.sha1).digest()]
            session_ctx.k2 = [ord(i) for i in hmac.new(_sik_digest, b'\x02' * 20, hashlib.sha1).digest()]

        elif request.payload_type == 0x00:
            self.payload_type = 0x00
            self.bmc.debug('<< RMCP+ IPMI Response')

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

            # Note: will also need to check/generate the integrity piece for this response,
            # but that needs the body and header to be created already. as such, it happens
            # after the header generation, below.

        else:
            raise ValueError('Failed to build response - unknown payload type.')

        # build the list of bytes in the packet body - this will be used during response
        # header creation to generate the auth code and data length values
        self.set_body_from_state()

        # ----------------------
        # -- RESPONSE HEADER ---
        # ----------------------

        # use the same auth type in the response
        self.authentication_type = request.authentication_type

        self.is_authenticated = request.is_authenticated
        self.is_encrypted = request.is_encrypted

        # increment the session sequence number on the response, unless the current
        # sequence number is 0x00000000, since that tends to be the placeholder value
        seq = request.session_sequence_number
        if seq.count(0x00) != 4:
            seq = [seq[0] + 1] + seq[1:]
        self.session_sequence_number = seq

        if request.payload_type == 0x00:
            self.session_id = session_ctx.remote_session_id
        else:
            # use the same session id in the response
            self.session_id = request.session_id

        # set the length of the ipmi payload
        _len = len(self.body)
        self.payload_length = [(_len >> 0) & 0xff, (_len >> 8) & 0xff]

        # check if the packet requires encryption
        if self.is_encrypted:
            _data = self._body

            payload_size = len(_data)

            pad = (payload_size + 1) % 16
            if pad:
                pad = 16 - pad

            new_payload_size = (
                payload_size +  # size of the original payload
                pad +           # size of the pad
                1 +             # +1 for the byte specifying pad length
                16              # +16 for the bytes specifying cipher IV
            )

            self.payload_length = [(new_payload_size >> 0) & 0xff, (new_payload_size >> 8) & 0xff]

            self.iv = [random.randint(0, 255) for _ in range(16)]
            cipher = AES.new(''.join(map(chr, session_ctx.k2[0:16])), AES.MODE_CBC, ''.join(map(chr, self.iv)))
            encrypted = cipher.encrypt(''.join(map(chr, _aespad(_data))))
            self._body = self.iv + map(ord, encrypted)

        # set the packet header after encryption may occur, since the payload length will
        # change depending on whether or not encryption takes place.
        self.set_header_from_state()

        # check if the packet requires an integrity check
        if self.is_authenticated:

            # will want to check integrity algorithm here, now that the header and body have
            # been built.
            _tmp_pkt = self.header + self.body

            needed_pad = (len(_tmp_pkt) - 2) % 4
            if needed_pad:
                needed_pad = 4 - needed_pad
            pad = [0xff] * needed_pad

            # From the IPMI spec:
            #  Unless otherwise specified, the integrity algorithm is applied to the packet
            #  data starting with the auth type/format field up to and including the field
            #  that immediately precedes the auth code field itself.
            integrity_data = _tmp_pkt + pad + [needed_pad] + [0x07]

            _hmac = hmac.new(
                ''.join(map(chr, session_ctx.k1)),
                ''.join(map(chr, integrity_data)),
                hashlib.sha1
            )

            auth_code = map(ord, _hmac.digest())[:12]

            self._body += pad + [needed_pad] + [0x07] + auth_code


def _aespad(data):
    """ To conform with AES CBC encryption, the encrypted payload needs
    to be a multiple of 16, so it may need to be padded (see table
    table 13-20 AES-CBC encrypted payload fields).

    derived from:
    https://github.com/openstack/pyghmi/blob/master/pyghmi/ipmi/private/session.py#L240
    """
    # need to count the pad length field as well, hence the +1
    needed_pad = (len(data) + 1) % 16
    if needed_pad:
        needed_pad = 16 - needed_pad

    # offset by one so the padding starts with a value of 0x01
    pad = [i for i in range(1, needed_pad + 1)]
    # create the padded value, adding in the pad length at the end
    new_data = data + pad + [needed_pad]
    return new_data
