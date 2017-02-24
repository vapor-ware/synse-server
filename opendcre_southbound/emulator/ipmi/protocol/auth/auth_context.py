#!/usr/bin/env python
""" Context object used to track state between the BMC and remote client
for a given session.

    Author: Erick Daniszewski
    Date:   09/06/2016
    
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
from auth_base import IPMIAuthType


class SessionContext(IPMIAuthType):
    """
    FIXME - the 'IPMIAuthType' class was named early on during model development here.
    While this context is not an 'auth type', the base class does contain all of the fields
    available for the context to store, so it is convenient to use. in the future, it
    may make sense to re-name / re-organize things a bit so that the naming of objects in
    the class hierarchy make a bit more sense.

    This is ultimately just a thin wrapper around the base class to make its purpose
    better-known.
    """
    def __init__(self, ipmi_packet):
        super(SessionContext, self).__init__(ipmi_packet)

    def update_ctx(self):
        pass

    def parse(self):
        pass

    def set_body_from_state(self):
        pass

    def build_response(self, request, response_data, raw_data):
        pass

    def set_header_from_state(self):
        pass
