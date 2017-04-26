#!/usr/bin/env python
""" Synse Version

    Author: Erick Daniszewski
    Date:   26 April 2017

    \\//
     \/apor IO
"""

# FIXME : this is already defined in the synse-server/opendcre subdirectory.
# it should not be defined here as well!! we either need to:
#   1. be able to share info, such as version info, between the two components
#   2. do some fancier NGINX rewrites to obviate the need for version info here
#
# Point 1 is perhaps a bit messy, but is nice in that it ties the graphql
# version with the synse version that it acts against.
#
# Option 2 is nice in that it keeps things clean here, but we effectively
# become version agnostic, since NGINX won't do a version check.

__version_major__ = "1"
__version_minor__ = "3"
__version_micro__ = "0"
__api_version__ = __version_major__ + "." + __version_minor__
__version__ = __api_version__ + "." + __version_micro__
