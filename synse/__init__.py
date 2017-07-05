#!/usr/bin/env python
""" Vapor IO Synse Server package.

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


__title__ = 'synse'
# FIXME: will need to re-work how versioning works in synse. currently, this
#   is unused. see the VERSION file at the project root for the true version.
__version__ = '1.4.0'

__description__ = 'Synse Server'
__author__ = 'Vapor IO'
__author_email__ = 'eng@vapor.io'
__url__ = 'https://github.com/vapor-ware/synse-server'


if __name__ == '__main__':
    print(__version__)
