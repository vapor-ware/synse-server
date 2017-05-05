""" Schema for GraphQL

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

import functools

import graphene

from . import device, util
from .rack import Rack


def get_device_types():
    return [getattr(device, x) for x in dir(device) if x.endswith('Device')]


def create():
    return graphene.Schema(
        query=Cluster,
        auto_camelcase=False,
        types=get_device_types()
    )


class Cluster(graphene.ObjectType):

    # Schema
    racks = graphene.List(
        lambda: Rack,
        required=True,
        id=graphene.String()
    )

    @functools.lru_cache(maxsize=1)
    def _request_assets(self):
        return dict([(k, '') for k in self._assets])

    @graphene.resolve_only_args
    def resolve_racks(self, id=None):
        return [Rack.build(self, r)
                for r in util.arg_filter(
                    id,
                    lambda x: x.get('rack_id') == id,
                    util.make_request('scan').get('racks'))]
