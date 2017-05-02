#!/usr/bin/env python
""" GraphQL Frontend

    Author:  Thomas Rampelberg
    Date:    2/24/2017

    \\//
     \/apor IO
"""

from graphql_frontend import config
from graphql_frontend import app, setup_logging


config.parse_args()
setup_logging()
