#!/usr/bin/env python
""" OpenDCRE IPMI Common Components.

    Author:  andrew
    Date:    9/29/2016

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
from opendcre_southbound.definitions import BMC_PORT
from pyghmi.ipmi import command


class IpmiCommand(object):
    """ Wrapper for IPMICommand that cleans up after itself.
    """

    def __init__(self, username=None, password=None, ip_address=None, port=BMC_PORT):
        self.o = command.Command(userid=username, password=password, bmc=ip_address, port=port)

    def __enter__(self):
        return self.o

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'o') and self.o:
            self.o.ipmi_session.logout()
