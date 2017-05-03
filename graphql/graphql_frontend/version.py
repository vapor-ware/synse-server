#!/usr/bin/env python
""" Synse Version

    Author: Erick Daniszewski
    Date:   26 April 2017

    \\//
     \/apor IO
"""
from __future__ import print_function
import logging
import os

logger = logging.getLogger(__name__)


file_name = 'VERSION'

pwd = os.path.dirname(os.path.abspath(__file__))
version_file = os.path.abspath(os.path.join(pwd, '..', '..', file_name))

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
