""" Rack Schema

    Author: Thomas Rampelberg
    Date:   2/27/2017

    \\//
     \/apor IO
"""

import functools

import graphene

from . import util
from .. import config
from .board import Board


@util.resolve_assets
class Rack(graphene.ObjectType):
    _assets = [
        "failed_servers",
        "server_count"
    ]
    _parent = None

    id = graphene.String(required=True)
    rack_id = graphene.String(required=True)

    # routing table
    is_leader = graphene.Boolean(required=True)
    is_shadow = graphene.Boolean(required=True)
    vec_ip = graphene.String(required=True)

    # asset
    failed_servers = graphene.String(required=True)
    server_count = graphene.String(required=True)

    boards = graphene.List(
        lambda: Board,
        required=True,
        id=graphene.String())

    @functools.lru_cache(maxsize=1)
    def _request_assets(self):
        if config.options.get('mode') == 'opendcre':
            return {
                "failed_servers": "",
                "server_count": ""
            }

        return util.make_request(
            "asset/{0}/{1}".format(self._parent.id, self.id))

    def get_asset(self, asset, *args, **kwargs):
        return self._request_assets().get(asset, "")

    def _rack_info(self):
        for rack in filter(lambda x: x.get("rack_id") == self.id,
                           self._parent._routing.get('racks')):
            return rack

        raise Exception("Rack ID does not exist.")

    def get_boards(self):
        if config.options.get('mode') == 'opendcre':
            return self._rack_info().get("boards")

        return util.make_request(
            "inventory/{0}/{1}".format(self._parent.id, self.id)
            ).get("clusters", [])[0].get("racks")[0].get("boards")

    @staticmethod
    def build(parent, info):
        _id = info["rack_id"]

        if config.options.get('mode') == 'opendcre':
            info.update({
                "is_leader": False,
                "is_shadow": False,
                "vec_ip": ""
            })

        return Rack(id=_id, _parent=parent, **info)

    @graphene.resolve_only_args
    def resolve_boards(self, id=None):
        return [Board.build(self, b)
                for b in util.arg_filter(
                    id,
                    lambda x: x.get("board_id") == id,
                    self.get_boards())]
