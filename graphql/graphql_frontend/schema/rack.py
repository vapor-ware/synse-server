""" Rack Schema

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
        return self._info.get('boards')

    @staticmethod
    def build(parent, info):
        _id = info['rack_id']

        return Rack(id=_id, _parent=parent, _info=info, **info)

    @graphene.resolve_only_args
    def resolve_boards(self, id=None):
        return [Board.build(self, b)
                for b in util.arg_filter(
                    id,
                    lambda x: x.get('board_id') == id,
                    self.get_boards())]
