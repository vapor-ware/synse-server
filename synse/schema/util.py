""" Utils to help out with building schemas

    Author: Thomas Rampelberg
    Date:   2/27/2017

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
import functools

import requests
import requests.compat

from synse.version import __api_version__

SESSION = requests.Session()

logger = logging.getLogger(__name__)


def make_request(url):
    base = 'http://{0}/synse/{1}/'.format(
        '0.0.0.0:5000', __api_version__)
    logger.debug('>> REQUEST URL: {}'.format(requests.compat.urljoin(base, url)))
    result = SESSION.get(requests.compat.urljoin(base, url))
    result.raise_for_status()
    return result.json()


def get_asset(self, asset, *args, **kwargs):
    """Fetch the value for a specific asset.

    Gets converted into resolve_asset_name(). See _assets for the list that
    are using this method as resolve.
    """
    return self._request_assets().get(asset, '')


# FIXME -- unused?
def resolve_assets(cls):
    """Decorator to dynamically resolve fields.

    Add resolve methods for everything in _assets.
    """
    for asset in cls._assets:
        setattr(
            cls,
            'resolve_{0}'.format(asset),
            partialmethod(get_asset, asset))
    return cls


def arg_filter(val, fn, lst):
    if val is not None:
        return filter(fn, lst)
    return lst


def partialmethod(f, *args, **kwargs):
    @functools.wraps(f)
    def partial(self, *pargs, **pkwargs):
        _kwargs = kwargs.copy()
        _kwargs.update(pkwargs)
        return f(self, *(args + pargs), **_kwargs)
    return partial
