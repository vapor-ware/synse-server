#!/usr/bin/env python
""" Redfish Authentication class

RfAuthentication class, supports basic HTTP authentication with
hardcoded username=root and password=redfish. Also supports
authentication via session token. To request session token from
emulator, send a POST request to /redfish/v1/SessionService/Sessions.
Response will include X-Auth-Token.

This was based off of DMTF's Redfish-Profile-Simulator (see LICENSE.txt
in the redfish emulator directory, and attribution, below) -
https://github.com/DMTF/Redfish-Profile-Simulator

    Author:  Linh Hoang
    Date:    02/09/17

    \\//
     \/apor IO

-------------------------------------------------------

Copyright (c) 2016, Contributing Member(s) of Distributed
Management Task Force, Inc.. All rights reserved.

Redistribution and use in source and binary forms, with or
without modification, are permitted provided that the following
conditions are met:

- Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.
- Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in
  the documentation and/or other materials provided with the distribution.
- Neither the name of the Distributed Management Task Force (DMTF)
  nor the names of its contributors may be used to endorse or promote
  products derived from this software without specific prior written
 permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED
AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
DAMAGE.
"""

from functools import wraps

from flask import request


class RfAuthentication(object):
    """Redfish emulator authentication.
    """

    def __init__(self):
        self.verify_password(None)
        self.verify_token(None)

    def verify_password(self, f):
        """ Verify a password
        """
        self.password_callback = f
        return f

    def verify_token(self, f):
        """ Verify a token
        """
        self.token_callback = f
        return f

    def auth_required(self, f):
        """ Decorator to denote that a resouce requires authentication.
        """
        @wraps(f)
        def decorated(*args, **kwargs):  # pylint: disable=missing-docstring
            auth = request.authorization
            if auth is None:
                auth_token = request.headers.get('X-Auth-Token')
                if self.token_callback(auth_token) is not True:
                    return 'Access denied, failed to authenticate access token in header.', 401
            if auth is not None:
                if self.password_callback(auth.username, auth.password) is not True:
                    return 'Access denied, failed to authenticate username and password.', 401
            return f(*args, **kwargs)
        return decorated
