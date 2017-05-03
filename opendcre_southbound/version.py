#!/usr/bin/env python
""" Vapor CORE Centralized Version Configuration

*** Version information should be updated here for each new build***

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
import logging
import os

logger = logging.getLogger(__name__)


file_name = 'VERSION'

pwd = os.path.dirname(os.path.abspath(__file__))
version_file = os.path.abspath(os.path.join(pwd, '..', file_name))

# if we are unable to locate or read the version file, we will fail hard
# after logging a message. a version number is needed to properly
# generate the API endpoints, among other things, so without it the
# service should not run.
try:
    with open(version_file, 'r') as f:
        v = f.read()

except Exception:
    logger.error(
        'Unable to determine version. VERSION file must exist in the '
        'project root and should have the format: major.minor.micro'
    )
    raise


_version = v.split('.')

if len(_version) != 3:
    raise ValueError(
        'The version specified in the VERSION file must have the format: '
        'major.minor.micro.'
    )


__version_major__ = _version[0]
__version_minor__ = _version[1]
__version_micro__ = _version[2]
__api_version__ = __version_major__ + '.' + __version_minor__
__version__ = __api_version__ + '.' + __version_micro__

if __name__ == '__main__':
    print(__version__)
