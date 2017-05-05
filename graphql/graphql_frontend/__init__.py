#!/usr/bin/env python
""" GraphQL Frontend

    Author:  Thomas Rampelberg
    Date:    2/24/2017

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

import json
import logging.config
import os

from flask import Flask, jsonify
from flask_graphql import GraphQLView

import graphql_frontend.config
import graphql_frontend.schema
import graphql_frontend.version


def setup_logging(name='logging.json'):
    path = os.path.join(os.path.dirname(__file__), '..', name)
    with open(path, 'rt') as f:
        config = json.load(f)
    logging.config.dictConfig(config)


app = Flask(__name__)


local_schema = graphql_frontend.schema.create()
PREFIX = '/synse/{}'.format(graphql_frontend.version.__api_version__)


@app.route(PREFIX + '/graphql/test', methods=['GET', 'POST'])
def test_routine():
    """ Test routine to verify the endpoint is running and ok
    without relying on other dependencies.
    """
    return jsonify({'status': 'ok'})


app.add_url_rule(
    PREFIX + '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=local_schema,
        graphiql=True)
)


def main():
    app.run(host='0.0.0.0', port=graphql_frontend.config.options.get('port'))


if __name__ == '__main__':
    main()
