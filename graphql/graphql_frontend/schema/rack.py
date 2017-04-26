""" Rack Schema

    Author: Thomas Rampelberg
    Date:   2/27/2017

    \\//
     \/apor IO
"""

import graphene

from . import util
from .board import Board


class Rack(graphene.ObjectType):
    _info = None
    _parent = None

    id = graphene.String(required=True)
    rack_id = graphene.String(required=True)

    boards = graphene.List(
        lambda: Board,
        required=True,
        id=graphene.String())

    def get_boards(self):
        return self._info.get("boards")

    @staticmethod
    def build(parent, info):
        _id = info["rack_id"]

        return Rack(id=_id, _parent=parent, _info=info, **info)

    @graphene.resolve_only_args
    def resolve_boards(self, id=None):
        return [Board.build(self, b)
                for b in util.arg_filter(
                    id,
                    lambda x: x.get("board_id") == id,
                    self.get_boards())]
