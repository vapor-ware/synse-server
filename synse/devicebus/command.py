#!/usr/bin/env python
""" A general Command object which models a Synse command to be handled by
a devicebus implementation.

Each Synse endpoint will generate a Command object and will pass it along
to the appropriate devicebus interface. It is left to the interface to
handle (or refuse to handle) the command.

    Author: Erick Daniszewski
    Date:   09/15/2016
    
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
from response import Response


class Command(object):
    """ Model for a generic Synse command.
    """

    def __init__(self, cmd_id, data, sequence):
        """ Constructor for a new Command instance.

        Args:
            cmd_id (int): the integer id which specifies the command type.
            data (dict): the context data associated with the command.
            sequence (int): the sequence number of the command.
        """
        self.cmd_id = cmd_id
        self.data = data
        self.sequence = sequence

    def make_response(self, data):
        """ Make a Response object which contains a devicebus implementation's
        response to the given Command.

        Args:
            data (dict): a dictionary containing the response data.

        Returns:
            Response: a Response object wrapping the given data.
        """
        return Response(self, data)
