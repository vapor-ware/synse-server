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

import graphene
from pylru import lrudecorator

from . import device, util
from .rack import Rack


def get_device_types():
    """ Get the device types that exist in the `device` module.

    Returns:
        list: a list of the supported device types.
    """
    return [getattr(device, x) for x in dir(device) if x.endswith('Device')]


def create():
    """ Create a graphene schema for our graphql endpoints.

    Returns:
         graphene.Schema: the schema created for our graphql endpoints.
    """
    return graphene.Schema(
        query=Cluster,
        auto_camelcase=False,
        types=get_device_types()
    )


class Cluster(graphene.ObjectType):
    """ Model for a cluster of racks.
    """

    # Schema
    racks = graphene.List(
        lambda: Rack,
        required=True,
        id=graphene.String()
    )

    @lrudecorator(1)
    def _request_assets(self):
        """ Get the assets of the cluster.

        Returns:
            dict: a dictionary of assets mapped to empty strings.
        """
        return dict([(k, '') for k in self._assets])

    @graphene.resolve_only_args
    def resolve_racks(self, id=None):
        """ Resolve the racks that belong to the cluster.

        Args:
            id (str): the id of the rack to filter upon.

        Returns:
            list[Rack]: a list of Rack objects that belong to the
                cluster.
        """
        return [Rack.build(self, r)
                for r in util.arg_filter(
                    id,
                    lambda x: x.get('rack_id') == id,
                    util.make_request('scan').get('racks'))]
