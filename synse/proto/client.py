"""Synse Server Python client for communicating to plugins via the gRPC API."""

import os

import grpc
import synse_grpc

from synse import config
from synse.const import SOCKET_DIR
from synse.i18n import _
from synse.log import logger


class WriteData:
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
            synse_grpc.api.WriteData: The gRPC model of the WriteData object.
        """
        return synse_grpc.api.WriteData(
            action=self.action,
            data=self.data
        )


class PluginClient:
    """The `PluginClient` class provides an interface to Synse Plugins
    via the Synse Plugin gRPC API.

    There should be one instance of a `PluginClient` for every plugin
    that is registered with Sysnse Server.

    This class is a base class and should not be initialized directly.

    Args:
        address (str): The address of the Plugin.
    """

    type = None

    def __init__(self, address):
        self.address = address
        self.channel = None
        self.grpc = None

        self.make_stub()

    def _fmt_address(self):
        """Format the client address appropriately, based on the network
        type of the client.
        """
        raise NotImplementedError('Subclasses must implement their own address formatting.')

    def make_channel(self):
        """Make the channel for the grpc client stub."""
        # If Synse Server is configured to communicate with the plugin using
        # TLS, set up a secure channel, otherwise use an insecure channel.
        # FIXME (etd) - we'll probably want to support using a CA here?
        if config.options.get('grpc.tls'):
            logger.info(_('TLS enabled for gRPC'))

            cert = config.options.get('grpc.tls.cert')
            logger.info(_('Using cert file: {}').format(cert))
            with open(cert, 'rb') as f:
                plugin_cert = f.read()

            creds = grpc.ssl_channel_credentials(root_certificates=plugin_cert)
            self.channel = grpc.secure_channel(self._fmt_address(), creds)
        else:
            self.channel = grpc.insecure_channel(self._fmt_address())

    def make_stub(self):
        """Create the gRPC client stub to communicate with the plugin."""
        self.make_channel()
        self.grpc = synse_grpc.grpc.PluginStub(self.channel)

    def test(self):
        """Test that the plugin is reachable

        Returns:
            synse_grpc.api.Status: The status of the 'test' ping. This
                should always resolve to 'ok' if the plugin is reachable,
                or else result in a timeout/connection failure.
        """
        logger.debug(_('Issuing gRPC test request'))

        req = synse_grpc.api.Empty()
        timeout = config.options.get('grpc.timeout', None)
        resp = self.grpc.Test(req, timeout=timeout)
        return resp

    def health(self):
        """Get the health of the plugin.

        Returns:
            synse_grpc.api.PluginHealth: The snapshot of the plugin's
                health at the time the request was made.
        """
        logger.debug(_('Issuing gRPC health request'))

        req = synse_grpc.api.Empty()
        timeout = config.options.get('grpc.timeout', None)
        resp = self.grpc.Health(req, timeout=timeout)
        return resp

    def metainfo(self):
        """Get the plugin metainfo.

        Returns:
            synse_grpc.api.Metadata: The plugin's metadata.
        """
        logger.debug(_('Issuing gRPC metainfo request'))

        req = synse_grpc.api.Empty()
        timeout = config.options.get('grpc.timeout', None)
        resp = self.grpc.Metainfo(req, timeout=timeout)
        return resp

    def capabilities(self):
        """Get the plugin device capabilities.

        Returns:
            list[synse_grpc.api.DeviceCapability]: All device capability
                information provided by the plugin.
        """
        logger.debug(_('Issuing gRPC capabilities request'))

        req = synse_grpc.api.Empty()
        timeout = config.options.get('grpc.timeout', None)
        resp = [c for c in self.grpc.Capabilities(req, timeout=timeout)]
        return resp

    def devices(self, rack=None, board=None):
        """Get all device information from a plugin.

        Args:
            rack (str): The rack to filter by.
            board (str): The board to filter by.

        Returns:
            list[synse_grpc.api.Device]: All device information
                provided by the plugin.
        """
        logger.debug(_('Issuing gRPC devices request'))

        # If the rack or board is not specified, pass it through as an
        # empty string.
        rack = rack if rack is not None else ''
        board = board if board is not None else ''

        req = synse_grpc.api.DeviceFilter(
            rack=rack,
            board=board
        )

        timeout = config.options.get('grpc.timeout', None)
        resp = [r for r in self.grpc.Devices(req, timeout=timeout)]

        return resp

    def read(self, rack, board, device):
        """Get a reading from the specified device.

        Args:
            rack (str): The rack which the device resides on.
            board (str): The board which the device resides on.
            device (str): The identifier for the device to read.

        Returns:
            list[synse_grpc.api.Reading]: The reading responses for the
                specified device, if it exists.
        """
        logger.debug(_('Issuing gRPC read request'))

        req = synse_grpc.api.DeviceFilter(
            device=device,
            board=board,
            rack=rack,
        )

        timeout = config.options.get('grpc.timeout', None)
        resp = [r for r in self.grpc.Read(req, timeout=timeout)]

        return resp

    def write(self, rack, board, device, data):
        """Write data to the specified device.

        Args:
            rack (str): The rack which the device resides on.
            board (str): The board which the device resides on.
            device (str): The identifier for the device to write to.
            data (list[WriteData]): The data to write to the device.

        Returns:
            synse_grpc.api.Transactions: The transactions that can be used
                to track the given write request(s).
        """
        logger.debug(_('Issuing gRPC write request'))

        req = synse_grpc.api.WriteInfo(
            deviceFilter=synse_grpc.api.DeviceFilter(
                device=device,
                board=board,
                rack=rack,
            ),
            data=[d.to_grpc() for d in data]
        )

        timeout = config.options.get('grpc.timeout', None)
        resp = self.grpc.Write(req, timeout=timeout)
        return resp

    def transaction(self, transaction_id):
        """Check the state of a write transaction.

        Args:
            transaction_id (str): The ID of the transaction to check.

        Returns:
            list[synse_grpc.api.WriteResponse]: The WriteResponse detailing the
                status and state of the given write transaction.
        """
        logger.debug(_('Issuing gRPC transaction request'))

        req = synse_grpc.api.TransactionFilter(
            id=transaction_id
        )

        timeout = config.options.get('grpc.timeout', None)
        resp = [r for r in self.grpc.Transaction(req, timeout=timeout)]
        return resp


class PluginTCPClient(PluginClient):
    """A client for interfacing with Synse Plugins via TCP."""

    type = 'tcp'

    def _fmt_address(self):
        return self.address


class PluginUnixClient(PluginClient):
    """A client for interfacing with Synse Plugins via Unix socket."""

    type = 'unix'

    def _fmt_address(self):
        return 'unix:{}'.format(os.path.join(SOCKET_DIR, self.address))
