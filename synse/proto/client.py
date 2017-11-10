"""Synse Server python client for communicating to plugins via the gRPC API.
"""

import os

import grpc
from synse_plugin import api as synse_api
from synse_plugin import grpc as synse_grpc

from synse.const import BG_SOCKS
from synse.log import logger


class WriteData(object):
    """The WriteData object is a convenient way to group together
    write actions and raw data into a single bundle for a single write
    transaction.

    Multiple WriteData can be specified for a gRPC Write command, e.g.
    it may be the case for an LED that we want to turn it on and change
    the color simultaneously. This can be done with two WriteData objects
    passed in a list to the `SynseInternalClient.write` method, e.g.

      color = WriteData(action='color', raw=[b'ffffff'])
      state = WriteData(action='on')
    """

    def __init__(self, action=None, raw=None):
        """Constructor for the WriteData object.

        Args:
            action (str): the action string for the write.
            raw (list[bytes]): a list of bytes that constitute the raw data
                that will be written by the write request.
        """
        self.action = action
        self.raw = raw

    def to_grpc(self):
        """Convert the WriteData model into the gRPC model for WriteData.

        Returns:
            synse_api.WriteData: the gRPC model of the WriteData object.
        """
        return synse_api.WriteData(
            action=self.action if self.action is not None else '',
            raw=self.raw if self.raw is not None else []
        )


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

    def read(self, rack, board, device):
        """Get a reading from the specified device.

        Args:
            rack (str): The rack which the device resides on.
            board (str): The board which the device resides on.
            device (str): The identifier for the device to read.
        """
        req = synse_api.ReadRequest(
            device=device,
            board=board,
            rack=rack
        )

        resp = []
        for r in self.stub.Read(req):
            resp.append(r)

        return resp

    def metainfo(self, rack=None, board=None):
        """Get all meta-information from a plugin.

        Args:
            rack (str): The rack to filter by.
            board (str): The board to filter by.
        """
        # if the rack or board is not specified, pass it through as an
        # empty string.
        rack = rack if rack is not None else ''
        board = board if board is not None else ''

        req = synse_api.MetainfoRequest(
            rack=rack,
            board=board
        )

        resp = []
        for r in self.stub.Metainfo(req):
            resp.append(r)

        return resp

    def write(self, rack, board, device, data):
        """Write data to the specified device.

        Args:
            rack (str): The rack which the device resides on.
            board (str): The board which the device resides on.
            device (str): The identifier for the device to write to.
            data (list[WriteData]): The data to write to the device.
        """
        req = synse_api.WriteRequest(
            device=device,
            board=board,
            rack=rack,
            data=[d.to_grpc() for d in data]
        )

        resp = self.stub.Write(req)
        return resp

    def check_transaction(self, transaction_id):
        """Check the state of a write transaction.

        Args:
            transaction_id (str): The ID of the transaction to check.
        """
        req = synse_api.TransactionId(
            id=transaction_id
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
