#!/usr/bin/env python
""" Synse Exceptions

    Author:  Erick Daniszewski
    Date:    11/16/2015

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

# region Internal Exceptions


class SynseInternalException(Exception):
    """ Generic base for internal Synse exceptions.
    """


class BusTimeoutException(SynseInternalException):
    """ Exception raised when a PLC command fails to receive a response from
    the device bus. This may be for many reasons, which may be difficult or
    impossible to pinpoint, so no more specific error is available.
    """
    pass


class BusDataException(SynseInternalException):
    """ Exception raised either when the client requests an invalid state or
    when a PLC device responds with an invalid packet.
    """
    pass


class ChecksumException(SynseInternalException):
    """ Exception raised when checksum validation fails on a PLC packet.
    ChecksumExceptions should use a retry mechanism to resend the packets.
    """
    pass


class BusCommunicationError(SynseInternalException):
    """ Exception raised when multiple retries fail after catching
    ChecksumExceptions.

    Corrupt data may slip through, raising the ChecksumException (which should
    then execute a retry mechanism). If corrupt data continues to get through
    such that the ChecksumException retry limit is reached, this exception
    should be thrown.
    """
    pass

# endregion

# region External Exceptions


class SynseException(Exception):
    """ Generic exception used for Synse endpoint exceptions.
    """


class CommandNotSupported(SynseException):
    """ Command is not supported by Synse.
    """
    pass

# endregion
