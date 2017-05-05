""" Configuration

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

import configargparse

parser = configargparse.ArgParser(default_config_files=[
    '/graphql_frontend/config.yaml'
])
parser.add('-c', '--my-config', is_config_file=True, help='config file path')
parser.add(
    '--port',
    env_var='PORT',
    default=5000,
    help='Port to listen on.')
parser.add(
    '--backend',
    env_var='BACKEND',
    default='localhost:5000',
    help='Path to the backend to use. example: "192.168.99.100:5000"')

options = None


def parse_args(opts=None):
    global options
    options = vars(parser.parse_args(opts))
