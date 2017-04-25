#!/usr/bin/env python
""" Query the GraphQL server

    Author:  Thomas Rampelberg
    Date:    3/16/2017

    \\//
     \/apor IO
"""

import argparse
import json
import os
import requests
import sys

import configargparse

description = """General tool for working with GraphQL from the command line.

- Looking for queries?
    - Run `query.py --list` to see what is there based off current config.

- Want to use your own JSON tool?
    - Output detects whether it is running in a TTY or not.
        Pipe to your tool of choice and it'll only get the raw JSON.

- Interested in using curl?
    - Get the raw JSON query: `query.py --query_output=json my_query`
======================================================================
"""

parser = configargparse.ArgParser(
    description=description,
    formatter_class=argparse.RawTextHelpFormatter)

# Output options
parser.add(
    '--list',
    action='store_true',
    help='Output all possible queries')
parser.add(
    '--query_output',
    choices=["graphql", "json"],
    help='Output only the query.')

# Server configuration
parser.add(
    '--server',
    default='localhost:5001',
    help='Server to send the query to.')

# Query location
parser.add(
    '--query_path',
    default='tests/queries',
    help='Path to the directory containing the queries you\'d like to use.')

# Actual query contents
parser.add(
    'query',
    nargs="?",
    help='Query to fetch')


def output_list(path):
    for (dirpath, dirnames, filenames) in os.walk(path):
        for f in sorted(filenames):
            base, ext = os.path.splitext(f)
            if ext != '.graphql':
                continue
            print(base)


def output_query(type, query):
    if type == 'graphql':
        print(query.get('query'))
    elif type == 'json':
        print(json.dumps(query))


def output_json(query):
    print(json.dumps(query))


def main(options):
    if options.get('list'):
        return output_list(options.get('query_path'))

    fname = os.path.join(
        options.get('query_path'),
        '{0}.graphql'.format(options.get('query')))

    if not os.path.exists(fname):
        print('ERROR: query does not exist at: {0}'.format(fname))
        print('Look at a list of available queries: ./get_query.py --list')
        sys.exit(1)

    with open(fname, "r") as myfile:
        content = myfile.read()

    query = {"query": content}

    if options.get('query_output') is not None:
        return output_query(options.get('query_output'), query)

    if sys.stdout.isatty():
        print('Query')
        print('-----')

        print(content)

    resp = requests.post(
        "http://{0}/graphql".format(options.get('server')), data=query)

    if sys.stdout.isatty():
        print('\nResult')
        print('-------')

    print(json.dumps(resp.json(), indent=4))


if __name__ == '__main__':
    main(vars(parser.parse_args()))
