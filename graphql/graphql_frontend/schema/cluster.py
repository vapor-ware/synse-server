""" Cluster Schema

    Author: Thomas Rampelberg
    Date:   2/27/2017

    \\//
     \/apor IO
"""

import functools

import graphene

from . import util
from .. import config
from .rack import Rack


@util.resolve_assets
class Cluster(graphene.ObjectType):
    _routing = None  # Needed to build the racks list and saves a request
    _assets = [
        "hardware_version",
        "leader_service_profile",
        "model_number",
        "serial_number",
        "vendor"
    ]

    # Schema
    id = graphene.String(required=True)
    racks = graphene.List(
        lambda: Rack,
        required=True,
        id=graphene.String()
    )

    hardware_version = graphene.String(required=True)
    leader_service_profile = graphene.String(required=True)
    model_number = graphene.String(required=True)
    serial_number = graphene.String(required=True)
    vendor = graphene.String(required=True)

    @functools.lru_cache(maxsize=1)
    def _request_assets(self):
        if config.options.get('mode') == 'opendcre':
            return dict([(k, '') for k in self._assets])

        return util.make_request(
            "asset/{0}".format(self.id)).get("cluster_info", {})

    @graphene.resolve_only_args
    def resolve_racks(self, id=None):
        if not self._routing:
            self._routing = util.make_request('scan')

        return [Rack.build(self, r)
                for r in util.arg_filter(
                    id,
                    lambda x: x.get("rack_id") == id,
                    self._routing["racks"])]
