#!/usr/bin/env python
""" Base for all protocols supported by the emulator to use.

    Author: Erick Daniszewski
    Date:   08/29/2016

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
import abc


class ProtocolBase(object):
    """ Base class for network protocol models used by the IPMI emulator.
    """
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        self.validate()

    @abc.abstractmethod
    def validate(self):
        """ Perform any validation actions needed for the given packet type.
        """
        pass

    @abc.abstractproperty
    def header(self):
        """ The packet header.
        """
        pass

    @abc.abstractproperty
    def body(self):
        """ The packet body.
        """
        pass
