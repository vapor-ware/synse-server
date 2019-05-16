#!/usr/bin/env python3
"""Entry point script for running Synse Server.

This script is installed as `synse_server` into /usr/local/bin (on macOS)
via the project's `setup.py` packaging. This is used to run Synse Server
by the official Docker image.

By default, the application is configured to listen on 0.0.0.0:5000. This
can be overridden via. command line arguments to the `synse_server` executable.
To see the usage information, you can pass in the --help flag.

Example usage:

    $ synse_server --host 0.0.0.0 --port 5000
"""

import argparse
import os
import sys

import synse_server
from synse_server.server import Synse


def main():
    parser = argparse.ArgumentParser(
        description='API server for the Synse platform',
    )
    parser.add_argument(
        '--host', required=False, default='0.0.0.0', type=str,
        help='the host/ip for the server to listen on',
    )
    parser.add_argument(
        '--port', required=False, default=5000, type=int,
        help='the port for the server to listen on',
    )
    parser.add_argument(
        '--version', required=False, action='store_true',
        help='print the version',
    )
    args = parser.parse_args()

    if args.version:
        os.write(sys.stdout, synse_server.__version__ + '\n')

    # Initialize and run a new instance of Synse Server.
    server = Synse(
        host=args.host,
        port=args.port,
    )
    server.run()


if __name__ == '__main__':
    main()
