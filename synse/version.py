#!/usr/bin/env python
""" Synse Version Configuration

    Author:  andrew
    Date:    7/23/2015

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

from __future__ import print_function

import sys

from synse import __version__

_version = __version__.split('.')

if len(_version) != 3:
    raise ValueError(
        'The version specified in the synse __init__ file must have '
        'the format: major.minor.micro.'
    )


major, minor, _ = _version

__api_version__ = major + '.' + minor

if __name__ == '__main__':
    args = sys.argv[1:]

    if args:
        if 'api' in args:
            print(__api_version__)
            exit()

    print(__version__)
