from __future__ import print_function

import os

import grpc

from synse.const import BG_SOCKS
from synse.log import logger

from synse_plugin import api as synse_api
from synse_plugin import grpc as synse_grpc


class SynseInternalClient(object):
    """ The `SynseInternalClient` object is a convenience wrapper around a
    grpc client used for communication between Synse and the background
    processes which are its data sources.

    There should be one instance of the `SynseInternalClient` for every
    configured background process.
    """

    _client_stubs = {}

    def __init__(self, name):
        """ Constructor for a `SynseInternalClient` instance.
        """
        self.name = name

        self.socket = self._socket()
        self.channel = self._channel()
        self.stub = self._stub()

        # add it to the tracked stubs
        SynseInternalClient._client_stubs[self.name] = self

    def _channel(self):
        """ Convenience method to create the client grpc channel. """
        return grpc.insecure_channel('unix:{}'.format(self.socket))

    def _socket(self):
        """ Convenience method to create the client grpc socket path. """
        return os.path.join(BG_SOCKS, self.name + '.sock')

    def _stub(self):
        """ Convenience method to create the grpc stub. """
        return synse_grpc.InternalApiStub(self.channel)

    @classmethod
    def get_client(cls, name):
        """ Get a client instance for the given name.

        Args:
            name (str): the name of the client. this is also the name
                given to the background process socket.

        Returns:
            SynseInternalClient: the client instance associated with
                that name. if a client does not exist for the given name,
                a new one will be created.
        """
        if name not in cls._client_stubs:
            SynseInternalClient(name)
        cli = cls._client_stubs[name]

        logger.debug('Getting Client:')
        logger.debug('  name: {}'.format(cli.name))
        logger.debug('  socket: {}'.format(cli.socket))
        logger.debug('  channel: {}'.format(cli.channel))
        logger.debug('  stub: {}'.format(cli.stub))
        return cli

    def read(self, device_id):
        """

        Args:
            device_id (str)
        """
        req = synse_api.ReadRequest(
            uid=str(device_id)
        )

        resp = []
        for r in self.stub.Read(req):
            resp.append(r)

        return resp

    def metainfo(self, rack=None, board=None):
        """

        Args:
            rack (str):
            board (str):
        """
        # if the rack or board is not specified, pass it through as an
        # empty string.
        rack = rack if rack is not None else ''
        board = board if board is not None else ''

        req = synse_api.MetainfoRequest(
            rack=str(rack),
            board=str(board)
        )

        resp = []
        for r in self.stub.Metainfo(req):
            resp.append(r)

        return resp

    def write(self, device_id, data):
        """

        Args:
            device_id (str):
            data (list[str]):
        """
        req = synse_api.WriteRequest(
            uid=device_id,
            data=data
        )

        resp = self.stub.Write(req)
        return resp

    def check_transaction(self, transaction_id):
        """

        Args:
            transaction_id (str):
        """
        req = synse_api.TransactionId(
            id=str(transaction_id)
        )

        resp = self.stub.TransactionCheck(req)
        return resp


def get_client(name):
    """ Get the internal client for the given process name.

    This is a convenience module-level wrapper around the
    `SynseInternalClient.get_client` method.

    Args:
        name (str): the name of the client. this is also the name
            given to the background process socket.

    Returns:
        SynseInternalClient: the client instance associated with
            that name. if a client does not exist for the given name,
            a new one will be created.
    """
    return SynseInternalClient.get_client(name)
