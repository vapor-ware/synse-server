#!/usr/bin/env python
""" RMCP ASF message class.

    Author: Erick Daniszewski
    Date:   08/29/2016
    
    \\//
     \/apor IO

-------------------------------
Copyright (C) 2015-17  Vapor IO

This file is part of OpenDCRE.

OpenDCRE is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 2 of the License, or
(at your option) any later version.

OpenDCRE is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenDCRE.  If not, see <http://www.gnu.org/licenses/>.
"""


class ASF(object):
    """ A lightweight wrapper around the RMCP ASF message format.

    For the emulator, this need only support the presence ping/pong messages
    as those are the only ASF messages we are likely to see.
    """
    def __init__(self, wrapper, raw_data):
        self.rmcp_wrapper = wrapper
        self.bmc = wrapper.bmc
        self.raw_data = raw_data

    def is_presence_ping(self):
        """ 80h:BFh Request or "Get" messages

        80h Presence Ping
        """
        message_type = self.raw_data[4]
        return message_type == chr(0x80)

    def is_capabilities_request(self):
        """ 80h:BFh Request or "Get" messages

        81h Capabilities Request
        """
        message_type = self.raw_data[4]
        return message_type == chr(0x81)

    def is_system_state_request(self):
        """ 80h:BFh Request or "Get" messages

        82h System State Request
        """
        message_type = self.raw_data[4]
        return message_type == chr(0x82)

    def is_open_session_request(self):
        """ 80h:BFh Request or "Get" messages

        83h Open Session Request
        """
        message_type = self.raw_data[4]
        return message_type == chr(0x83)

    def is_close_session_request(self):
        """ 80h:BFh Request or "Get" messages

        84h Close Session Request
        """
        message_type = self.raw_data[4]
        return message_type == chr(0x84)

    @classmethod
    def make_pong(cls, data=None):
        if data is None:
            data = []
        data_length = len(data)
        return [0x00, 0x00, 0x11, 0xbe, 0x40, 0x00, 0x00, data_length] + data
