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
import asyncio
import cProfile
import os
import sys

import uvloop

import synse_server
from synse_server.server import Synse


def main() -> None:
    uvloop.install()
    asyncio.set_event_loop(uvloop.new_event_loop())

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
    parser.add_argument(
        '--profile', required=False, action='store_true',
        help='profile synse server code execution,'
    )
    args = parser.parse_args()

    if args.version:
        os.write(sys.stdout, synse_server.__version__ + '\n')

    # Initialize and run a new instance of Synse Server.
    server = Synse(
        host=args.host,
        port=args.port,
    )

    if args.profile:
        print("""
        *************************
        Running in profiling mode
        -------------------------
        Synse Server was run with the --profile flag. This should only be used
        for development/debug. It should not be used in production.

        After Synse Server terminates, the profiling output will be printed out
        to console and written to file (synse-server.profile). If running in a
        container, it is your responsibility to copy the profile data out.
        *************************
        """)
        pr = cProfile.Profile()
        pr.enable()

        try:
            server.run()
        except Exception as e:
            print(f'Got exception: {e}')
        finally:
            pr.disable()

        pr.print_stats('cumulative')
        pr.dump_stats('synse-server.profile')

    else:
        server.run()


if __name__ == '__main__':
    main()
