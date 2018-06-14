"""Synse Server Python client for communicating to plugins via the gRPC API."""

import os

import grpc
from synse_plugin import api as synse_api
from synse_plugin import grpc as synse_grpc

from synse import config, errors
from synse.const import SOCKET_DIR
from synse.i18n import _
from synse.log import logger


class WriteData(object):
    """The WriteData object is a convenient way to group together
    write actions and raw data into a single bundle for a single write
    transaction.

    Multiple WriteData can be specified for a gRPC Write command, e.g.
    it may be the case for an LED that we want to turn it on and change
    the color simultaneously. This can be done with two WriteData objects
    passed in a list to the `SynsePluginClient.write` method, e.g.

        color = WriteData(action='color', data=b'ffffff')
        state = WriteData(action='on')

    Args:
        action (str): The action string for the write.
        data (bytes): The bytes that constitute the raw data that
            will be written by the write request.
    """

    def __init__(self, action=None, data=None):
        self.action = action if action is not None else ''
        self.data = data if data is not None else b''

    def __str__(self):
        return '<WriteData: action: {}, raw: {}>'.format(self.action, self.data)

    def to_grpc(self):
        """Convert the WriteData model into the gRPC model for WriteData.

        Returns:
            synse_plugin.api.WriteData: The gRPC model of the WriteData object.
        """
        return synse_api.WriteData(
            action=self.action,
            data=self.data
        )


class SynsePluginClient(object):
    """The `SynsePluginClient` object is a convenience wrapper around a
    gRPC client used for communication between Synse and the background
    processes which are its data sources.

    There should be one instance of the `SynsePluginClient` for every
    configured background process.

    Args:
        name (str): The name of the Plugin which the client is used by.
        address (str): The Plugin address.
        mode (str): The communication mode of the Plugin (e.g. 'unix', 'tcp')
    """

    _client_stubs = {}

    def __init__(self, name, address, mode):
        self.name = name
        self.addr = address
        self.mode = mode

        self.channel = self._channel()
        self.stub = self._stub()

        # Add this client instance to the tracked stubs. This allows a client
        # to be looked up by name from the class itself.
        SynsePluginClient._client_stubs[self.name] = self

    def _channel(self):
        """Convenience method to create the client gRPC channel."""
        if self.mode == 'unix':
            target = 'unix:{}'.format(os.path.join(SOCKET_DIR, self.name + '.sock'))
        elif self.mode == 'tcp':
            target = self.addr
        else:
            raise errors.InvalidArgumentsError(
                _('Invalid gRPC client mode: {}').format(self.mode)
            )

        logger.debug(_('Client gRPC channel: {}').format(target))
        return grpc.insecure_channel(target)

    def _stub(self):
        """Convenience method to create the gRPC stub."""
        return synse_grpc.PluginStub(self.channel)

    @classmethod
    def get_client(cls, name):
        """Get a client instance for the given name.

        Args:
            name (str): The name of the client. This is also the name
                given to the Plugin.

        Returns:
            SynsePluginClient: The client instance associated with
                the given name.
            None: The given name has no associated client.
        """
        return cls._client_stubs.get(name)

    @classmethod
    def register(cls, name, addr, mode):
        """Register a new client instance.

        Args:
            name (str): The name of the plugin for the client.
            addr (str): The address the plugin will communicate over.
            mode (str): The communication mode of the plugin (either
                'tcp' or 'unix').

        Returns:
            SynsePluginClient: The newly registered client instance.
        """
        SynsePluginClient(name, addr, mode)
        cli = cls._client_stubs[name]

        logger.debug(
            _('Registered client "{}" for mode "{}", address "{}"')
            .format(cli.name, cli.mode, cli.addr)
        )
        return cli

    def test(self):
        """Test that the plugin is reachable

        Returns:
            synse_plugin.api.Status: The status of the 'test' ping. This
                should always resolve to 'ok' if the plugin is reachable,
                or else result in a timeout/connection failure.
        """
        logger.debug(_('Issuing gRPC test request'))

        req = synse_api.Empty()
        timeout = config.options.get('grpc.timeout', None)
        resp = self.stub.Test(req, timeout=timeout)
        return resp

    def health(self):
        """Get the health of the plugin.

        Returns:
            synse_plugin.api.PluginHealth: The snapshot of the plugin's
                health at the time the request was made.
        """
        logger.debug(_('Issuing gRPC health request'))

        req = synse_api.Empty()
        timeout = config.options.get('grpc.timeout', None)
        resp = self.stub.Health(req, timeout=timeout)
        return resp

    def metainfo(self):
        """Get the plugin metainfo.

        Returns:
            synse_plugin.api.Metadata: The plugin's metadata.
        """
        logger.debug(_('Issuing gRPC metainfo request'))

        req = synse_api.Empty()
        timeout = config.options.get('grpc.timeout', None)
        resp = self.stub.Metainfo(req, timeout=timeout)
        return resp

    def capabilities(self):
        """Get the plugin device capabilities.

        Returns:
            list[synse_plugin.api.DeviceCapability]: All device capability
                information provided by the plugin.
        """
        logger.debug(_('Issuing gRPC capabilities request'))

        req = synse_api.Empty()
        timeout = config.options.get('grpc.timeout', None)
        resp = [c for c in self.stub.Capabilities(req, timeout=timeout)]
        return resp

    def devices(self, rack=None, board=None):
        """Get all device information from a plugin.

        Args:
            rack (str): The rack to filter by.
            board (str): The board to filter by.

        Returns:
            list[synse_plugin.api.Device]: All device information
                provided by the plugin.
        """
        logger.debug(_('Issuing gRPC devices request'))

        # If the rack or board is not specified, pass it through as an
        # empty string.
        rack = rack if rack is not None else ''
        board = board if board is not None else ''

        req = synse_api.DeviceFilter(
            rack=rack,
            board=board
        )

        timeout = config.options.get('grpc.timeout', None)
        resp = [r for r in self.stub.Devices(req, timeout=timeout)]

        return resp

    def read(self, rack, board, device):
        """Get a reading from the specified device.

        Args:
            rack (str): The rack which the device resides on.
            board (str): The board which the device resides on.
            device (str): The identifier for the device to read.

        Returns:
            list[synse_plugin.api.Reading]: The reading responses for the
                specified device, if it exists.
        """
        logger.debug(_('Issuing gRPC read request'))

        req = synse_api.DeviceFilter(
            device=device,
            board=board,
            rack=rack,
        )

        timeout = config.options.get('grpc.timeout', None)
        resp = [r for r in self.stub.Read(req, timeout=timeout)]

        return resp

    def write(self, rack, board, device, data):
        """Write data to the specified device.

        Args:
            rack (str): The rack which the device resides on.
            board (str): The board which the device resides on.
            device (str): The identifier for the device to write to.
            data (list[WriteData]): The data to write to the device.

        Returns:
            synse_plugin.api.Transactions: The transactions that can be used
                to track the given write request(s).
        """
        logger.debug(_('Issuing gRPC write request'))

        req = synse_api.WriteInfo(
            deviceFilter=synse_api.DeviceFilter(
                device=device,
                board=board,
                rack=rack,
            ),
            data=[d.to_grpc() for d in data]
        )

        timeout = config.options.get('grpc.timeout', None)
        resp = self.stub.Write(req, timeout=timeout)
        return resp

    def transaction(self, transaction_id):
        """Check the state of a write transaction.

        Args:
            transaction_id (str): The ID of the transaction to check.

        Returns:
            list[synse_plugin.api.WriteResponse]: The WriteResponse detailing the
                status and state of the given write transaction.
        """
        logger.debug(_('Issuing gRPC transaction request'))

        req = synse_api.TransactionFilter(
            id=transaction_id
        )

        timeout = config.options.get('grpc.timeout', None)
        resp = [r for r in self.stub.Transaction(req, timeout=timeout)]
        return resp


def get_client(name):
    """Get the internal client for the given plugin name.

    This is a convenience module-level wrapper around the
    `SynseInternalClient.get_client` method.

    Args:
        name (str): The name of the client. This is also the name
            given to the plugin socket, if configured for UNIX socket
            networking.

    Returns:
        SynsePluginClient: The client instance associated with
            that name. If a client does not exist for the given name,
            a new one will be created.
    """
    return SynsePluginClient.get_client(name)


def register_client(name, addr, mode):
    """Register a new internal client for a plugin.

    Args:
        name (str): The name of the plugin.
        addr (str): The address which the plugin communicates over.
        mode (str): The communication mode of the plugin (either
            'unix' or 'tcp').

    Returns:
        SynsePluginClient: The client instance associated with the
            name given. If a client does not exist for the given name,
            a new one will be created.
    """
    cli = SynsePluginClient.get_client(name)
    if cli is None:
        logger.debug(_('Registering new client for Plugin: {}').format(name))
        cli = SynsePluginClient.register(name, addr, mode)
    return cli
