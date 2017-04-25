""" Configuration

    Author:  Thomas Rampelberg
    Date:    2/24/2017

    \\//
     \/apor IO
"""

import configargparse
import sys


parser = configargparse.ArgParser(default_config_files=[
    "/graphql_frontend/config.yaml"
])
parser.add('-c', '--my-config', is_config_file=True, help='config file path')
parser.add(
    '--port',
    env_var='PORT',
    default=5001,
    help='Port to listen on.')
parser.add(
    '--backend',
    env_var='BACKEND',
    default='demo.vapor.io:5000',
    help='Path to the backend to use. example: "demo.vapor.io:5000"')
parser.add(
    '--username',
    env_var='AUTH_USERNAME',
    help='Username to use when authenticating against the router.')
parser.add(
    '--password',
    env_var='AUTH_PASSWORD',
    help='Password to use when authenticating against the router.')
parser.add(
    '--mode',
    env_var='MODE',
    default='opendcre',
    choices=['opendcre', 'core'],
    help='Either use OpenDCRE or CORE as a backend.')

options = None


def parse_args(opts=None):
    global options
    options = vars(parser.parse_args(opts))

    if options.get('mode') == 'core':
        if options.get('username') == '' or options.get('password') == '':
            print("Username and password must be set to use core mode.")
            sys.exit(1)
