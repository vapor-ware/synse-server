#!/usr/bin/env python
""" Vapor CORE Centralized Version Configuration

*** Version information should be updated here for each new build***

    Author:  andrew
    Date:    7/23/2015

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
from __future__ import print_function

__version_major__ = "1"
__version_minor__ = "3"
__version_micro__ = "0"
__api_version__ = __version_major__ + "." + __version_minor__
__version__ = __api_version__ + "." + __version_micro__

if __name__ == "__main__":
    print(__version__)
