"""
"""

import os
import socket
import time
from concurrent import futures

import grpc

from synse.emulator.src import devices
from synse.emulator.src.servicer import InternalApiServicer

from synse_plugin import grpc as synse_grpc

_ONE_DAY_IN_SECONDS = 60 * 60 * 24

SOCKET = '/synse/procs/emulator.sock'


def serve():
    """ Initialize, configure, and run the GRPC server.
    """
    # create the unix socket we will be communicating over
    try:
        os.remove(SOCKET)
    except OSError:
        pass

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(SOCKET)

    print('bound socket')

    print('making devices...')
    # first, read in device config and generate the device modeling
    devices.make_devices()

    # then, create and configure the grpc server
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    synse_grpc.add_InternalApiServicer_to_server(
        InternalApiServicer(), server
    )

    print('made server')

    server.add_insecure_port('unix:{}'.format(SOCKET))
    server.start()

    print('server started')

    # run the grpc server
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    serve()
