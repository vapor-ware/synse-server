#!/usr/bin/env python
""" Main blueprint for Synse. This contains the core endpoints
for Synse.

    Author: Erick Daniszewski
    Date:   09/24/2016

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

from flask import Blueprint, jsonify
from flask_graphql import GraphQLView

import synse.constants as const
from synse import schema
from synse.vapor_common.utils.endpoint import make_url_builder
from synse.version import __api_version__

# add the api_version to the prefix
PREFIX = const.endpoint_prefix + __api_version__
url = make_url_builder(PREFIX)

graphql = Blueprint('graphql', __name__)
logger = logging.getLogger(__name__)


local_schema = schema.create()
PREFIX = '/synse/{}'.format(__api_version__)


@graphql.route(PREFIX + '/graphql/test', methods=['GET', 'POST'])
def test_routine():
    """ Test routine to verify the endpoint is running and ok
    without relying on other dependencies.
    """
    return jsonify({'status': 'ok'})


graphql.add_url_rule(
    PREFIX + '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=local_schema,
        graphiql=True
    )
)
