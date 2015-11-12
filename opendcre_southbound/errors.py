#!/usr/bin/python
"""
   OpenDCRE Southbound Exceptions
   Author:  erick
   Date:    11/11/2015
        \\//
         \/apor IO

    Copyright (C) 2015  Vapor IO

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


class BusTimeoutException(Exception):
    """ Exception raised when a command fails to receive a response from the
    device bus. This may be for many reasons, which it may be difficult or
    impossible to pinpoint, so no more specific error is available.
    """
    pass


class BusDataException(Exception):
    """ Exception raised when something sent over the bus does not look right.
    """
    pass


class ChecksumException(Exception):
    """ Exception raised when checksum validation fails. ChecksumExceptions should
    use a retry mechanism to resend the packets.
    """
    pass


class CommunicationException(Exception):
    """ Exception raised when multiple retries fail after catching ChecksumExceptions.

    Corrupt data may slip through, raising the ChecksumException (which should then
    execute a retry mechanism). If corrupt data continues to get through such that the
    ChecksumException retry limit is reached, this exception should be thrown.
    """
    pass
