#!/usr/bin/env python
""" Vapor-specific errors and exceptions usable by all Vapor components.

    Author: Erick Daniszewski
    Date:   05/17/2016

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


class TestException(Exception):
    """An exception indicating a test failure."""
    pass  # Well hopefully not.


class VaporError(Exception):
    """ The base error class for all common Vapor errors.
    """
    pass


class RequestValidationError(VaporError):
    """ A request failed to validate identity hash headers.
    """
    pass


class VaporRequestError(VaporError):
    """ An error class which is raised fails for any reason, be it a connection
    error, timeout, etc.
    """
    pass


class VaporHTTPError(VaporError):
    """ An error class which wraps a `requests.Response` object and provides
    error information originating from that Response.

    This error is raised when a request does not fail, but the response contains
    a non-OK status code.
    """
    def __init__(self, response):
        """ Constructor for the `VaporHTTPError` object.

        Args:
            response (requests.Response): the response object related to the error.

        Returns:
            VaporHTTPError
        """
        self.response = response

    @property
    def status(self):
        """ Get the status code of the wrapped `requests.Response` object.
        """
        return self.response.status_code

    @property
    def json(self):
        """ Get the JSON data from the response, if any.
        """
        try:
            return self.response.json()
        except ValueError:
            return None

    @property
    def text(self):
        """ Get the text from the response, if any.
        """
        return self.response.text

    def __str__(self):
        """ The exceptions message.
        """
        json = self.json
        if json and 'message' in json:
            message = json['message']
        else:
            message = self.response.text

        return 'Request failure [HTTP {} ({}): {}] : {}'.format(
            self.response.status_code,
            self.response.reason,
            self.response.url,
            message
        )
