#!/usr/bin/env python
""" Vapor Common Endpoint Utilities

    Author: Erick Daniszewski
    Date:   13 Dec 2016

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

import logging
from functools import partial

logger = logging.getLogger(__name__)


def make_url_builder(base):
    """ Make a partial function that can be used to cleanly generate URLs.

    The partial function hides the common pieces of the URL leaving only
    the unique part -- the URI -- visible to the caller. This helps to
    keep endpoint definitions clean and readable.

    Args:
        base (str): the base of the URL which everything will be build off
            of - this is the common part of the URL.

    Returns:
        partial: a partial object that can be used to build urls.
    """
    def _url_builder(uri, url_base):  # pylint: disable=missing-docstring
        return url_base + uri
    return partial(_url_builder, url_base=base)
