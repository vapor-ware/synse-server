#!/usr/bin/env python
""" Context object used to track state between the BMC and remote client
for a given session.

    Author: Erick Daniszewski
    Date:   09/06/2016
    
    \\//
     \/apor IO
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
