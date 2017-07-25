#!/usr/bin/env python
""" Response object to model a devicebus implementation's response to
a given Command.

This model is used for validation (e.g. matching Commands with their Response)
and as a layer of abstraction around the response, so any other validation or
processing can happen here instead of being exposed in the Synse endpoint
logic.

    Author: Erick Daniszewski
    Date:   09/16/2016

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
import arrow


class Response(object):
    """ Model for a response to a generic Synse command.
    """

    def __init__(self, command, response_data):
        self.command = command
        self.cmd_id = command.cmd_id
        self.sequence = command.sequence

        # create a UTC timestamp for the response. note that this
        # is not the actual timestamp of the operation (e.g. read),
        # but the time at which the response is made, which is shortly
        # after the operation completes. since the timestamp granularity
        # is at the second level, the difference is negligible.
        self.timestamp = arrow.utcnow().timestamp

        self.data = response_data

    def get_response_data(self):
        """ Get the data that makes up the Response.

        This joins together the actual data from the operation with
        any metadata associated with the response, e.g. timestamp.

        Returns:
            dict: a dictionary of response data.
        """
        data = self.data
        if not data:
            data = {}
        return dict(timestamp=self.timestamp, **data)
