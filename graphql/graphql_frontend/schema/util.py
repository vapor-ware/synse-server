""" Utils to help out with building schemas

    Author: Thomas Rampelberg
    Date:   2/27/2017

    \\//
     \/apor IO
"""

import functools

import requests
import requests.compat

from graphql_frontend import config

SESSION = requests.Session()


def make_request(url):
    base = "http://{0}/opendcre/1.3/".format(
        config.options.get('backend'))
    result = SESSION.get(requests.compat.urljoin(base, url))
    result.raise_for_status()
    return result.json()


def get_asset(self, asset, *args, **kwargs):
    """Fetch the value for a specific asset.

    Gets converted into resolve_asset_name(). See _assets for the list that
    are using this method as resolve.
    """
    return self._request_assets().get(asset, "")


def resolve_assets(cls):
    """Decorator to dynamically resolve fields.

    Add resolve methods for everything in _assets.
    """
    for asset in cls._assets:
        setattr(
            cls,
            "resolve_{0}".format(asset),
            functools.partialmethod(get_asset, asset))
    return cls


def arg_filter(val, fn, lst):
    if val is not None:
        return filter(fn, lst)
    return lst
